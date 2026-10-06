"""Remote MCP with PostHog OAuth; exposes only bounded aggregate queries."""
import asyncio
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from cryptography.fernet import Fernet
from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.introspection import IntrospectionTokenVerifier
from fastmcp.server.dependencies import get_access_token
from key_value.aio.stores.filetree import FileTreeStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper

from reporting.posthog import PostHog
from reporting.queries import queries, report_metadata


def create_server(env=os.environ):
    origin = env['REPORT_POSTHOG_ORIGIN'].rstrip('/')
    public_origin = env['REPORT_PUBLIC_ORIGIN'].rstrip('/')
    project_id = int(env['REPORT_PROJECT_ID'])
    PostHog(origin, project_id, '')  # Validate origins before configuring endpoints.
    PostHog(public_origin, project_id, '')
    zone = env.get('REPORT_TIMEZONE', 'Europe/Moscow')
    ZoneInfo(zone)
    signing_key = env['REPORT_SIGNING_KEY']
    if len(signing_key) < 32:
        raise ValueError('REPORT_SIGNING_KEY must contain at least 32 random characters')
    redirects = json.loads(env['REPORT_REDIRECT_URIS'])
    if not isinstance(redirects, list) or not redirects or any(
            not isinstance(uri, str) or not uri.startswith('https://chatgpt.com/') or '*' in uri
            for uri in redirects):
        raise ValueError('Use exact ChatGPT HTTPS OAuth callback URLs')
    scopes = ['query:read', 'project:read']
    verifier = IntrospectionTokenVerifier(introspection_url=origin + '/oauth/introspect/',
        client_id=env['REPORT_OAUTH_CLIENT_ID'], client_secret=env['REPORT_OAUTH_CLIENT_SECRET'],
        required_scopes=scopes, timeout_seconds=15, cache_ttl_seconds=0)
    state = Path(env['REPORT_STATE_DIR'])
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    storage = FernetEncryptionWrapper(key_value=FileTreeStore(data_directory=state),
        fernet=Fernet(env['REPORT_STORAGE_KEY'].encode()))
    auth = OAuthProxy(upstream_authorization_endpoint=origin + '/oauth/authorize/',
        upstream_token_endpoint=origin + '/oauth/token/',
        upstream_revocation_endpoint=origin + '/oauth/revoke/',
        upstream_client_id=env['REPORT_OAUTH_CLIENT_ID'],
        upstream_client_secret=env['REPORT_OAUTH_CLIENT_SECRET'], token_verifier=verifier,
        base_url=public_origin, valid_scopes=scopes, client_storage=storage,
        jwt_signing_key=signing_key.encode(), allowed_client_redirect_uris=redirects,
        extra_authorize_params={'required_access_level': 'project'},
        token_endpoint_auth_method='client_secret_post', forward_pkce=True,
        # The upstream token's audience is PostHog, not this proxy's MCP resource.
        forward_resource=False, require_authorization_consent=True)
    server = FastMCP('AI Media Client Analytics', auth=auth)
    semaphore = asyncio.Semaphore(1)
    links = json.loads(env.get('REPORT_DASHBOARD_LINKS', '{}'))

    @server.tool(annotations={'readOnlyHint': True, 'destructiveHint': False,
                             'openWorldHint': False}, timeout=300)
    async def analytics_daily_report(report_day: str | None = None) -> dict:
        """Read yesterday and seven preceding complete days of product aggregates.

        report_day is an optional ISO date in the configured timezone, at most
        30 days old. Contains no event payloads, visitor/account IDs or arbitrary SQL.
        Empty datasets and missing coverage must be reported explicitly.
        """
        today = datetime.now(ZoneInfo(zone)).date()
        selected = date.fromisoformat(report_day) if report_day else today - timedelta(days=1)
        if not today - timedelta(days=30) <= selected < today:
            raise ValueError('Only completed days within the last 30 days can be requested')
        token = get_access_token()
        if token is None:
            raise RuntimeError('OAuth authentication is required')
        client = PostHog(origin, project_id, token.token)
        end = selected + timedelta(days=1)
        result = {'metadata': report_metadata(end, zone), 'dashboards': links, 'data': {}, 'errors': {}}
        async with semaphore:
            for name, sql in queries(end, zone=zone).items():
                try:
                    result['data'][name] = await asyncio.to_thread(client.query, sql)
                except RuntimeError as exc:
                    result['errors'][name] = str(exc)
        result['complete'] = not result['errors']
        return result

    @server.tool(annotations={'readOnlyHint': True, 'destructiveHint': False,
                             'openWorldHint': False})
    def analytics_dashboard_links() -> dict:
        """Return links to saved PostHog dashboards; does not query events."""
        return {'project_id': project_id, 'timezone': zone, 'dashboards': links}

    return server


if __name__ == '__main__':
    create_server().run(transport='http', host=os.environ.get('REPORT_BIND', '127.0.0.1'),
                        port=int(os.environ.get('REPORT_PORT', '8765')), show_banner=False)
