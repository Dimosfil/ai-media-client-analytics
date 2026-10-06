"""Run inside PostHog web container. Creates a single explicitly owned OAuth app.

Requires REPORT_OWNER_USER_ID, REPORT_PROJECT_ID, REPORT_POSTHOG_ORIGIN,
REPORT_PUBLIC_ORIGIN, REPORT_BOOTSTRAP_OUTPUT. Credentials are written only to
an exclusive 0600 file; never printed. Existing app or file is a hard refusal.
"""
import json
import os
import secrets
import shlex
from pathlib import Path
from urllib.parse import urlparse


def main():
    origin = os.environ['REPORT_PUBLIC_ORIGIN'].rstrip('/')
    upstream = os.environ['REPORT_POSTHOG_ORIGIN'].rstrip('/')
    for value in (origin, upstream):
        parsed = urlparse(value)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username:
            raise ValueError('Require HTTPS origins without paths or credentials')
    output = Path(os.environ['REPORT_BOOTSTRAP_OUTPUT'])
    if output.exists():
        raise RuntimeError('Bootstrap output exists; refusing secret replacement')
    if not os.environ.get('OIDC_RSA_PRIVATE_KEY'):
        raise RuntimeError('Configure a persistent OIDC_RSA_PRIVATE_KEY on PostHog web before registering OAuth')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posthog.settings')
    import django
    django.setup()
    from django.db import transaction
    from posthog.models import OrganizationMembership, Team, User
    from posthog.models.oauth import OAuthApplication
    fields = {field.name for field in OAuthApplication._meta.fields}
    if 'scopes' not in fields:
        raise RuntimeError('Runtime lacks OAuth application scope ceilings; do not deploy an unscoped fallback')
    team = Team.objects.get(pk=int(os.environ['REPORT_PROJECT_ID']))
    owner = User.objects.get(pk=int(os.environ['REPORT_OWNER_USER_ID']), is_active=True)
    if not OrganizationMembership.objects.filter(user=owner, organization=team.organization, level__gte=8).exists():
        raise RuntimeError('Explicit owner must be an administrator of this project organization')
    app_name = f'AI Media analytics reports (project {team.pk})'
    client_secret = secrets.token_urlsafe(48)
    settings = {
        'REPORT_POSTHOG_ORIGIN': upstream, 'REPORT_PUBLIC_ORIGIN': origin,
        'REPORT_PROJECT_ID': str(team.pk), 'REPORT_TIMEZONE': 'Europe/Moscow',
        'REPORT_OAUTH_CLIENT_SECRET': client_secret,
        'REPORT_SIGNING_KEY': secrets.token_urlsafe(48),
        'REPORT_STORAGE_KEY': __import__('base64').urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        'REPORT_STATE_DIR': '/var/lib/ai-media-analytics-report/oauth',
        'REPORT_REDIRECT_URIS': json.dumps(['https://chatgpt.com/connector_platform_oauth_redirect']),
        'REPORT_BIND': '127.0.0.1', 'REPORT_PORT': '8765', 'REPORT_DASHBOARD_LINKS': '{}',
    }
    with transaction.atomic():
        # Serialize setup per project so parallel runs cannot create duplicate apps.
        Team.objects.select_for_update().get(pk=team.pk)
        if OAuthApplication.objects.filter(organization=team.organization, name=app_name).exists():
            raise RuntimeError('OAuth app already exists; use the preserved secret or explicitly rotate it')
        app = OAuthApplication.objects.create(name=app_name, organization=team.organization, user=owner,
            client_type='confidential', authorization_grant_type='authorization-code',
            algorithm='RS256',
            client_secret=client_secret, redirect_uris=origin + '/auth/callback',
            scopes=['query:read', 'project:read'])
        if os.environ.get('REPORT_SET_PROJECT_TIMEZONE') == 'Europe/Moscow':
            team.timezone = 'Europe/Moscow'
            team.save(update_fields=['timezone'])
        settings['REPORT_OAUTH_CLIENT_ID'] = app.client_id
        fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                stream.write(''.join(f'{key}={shlex.quote(value)}\n' for key, value in settings.items()))
        except BaseException:
            output.unlink(missing_ok=True)
            raise
    print('OAuth application created; private bootstrap file written. No tokens granted yet.')


if __name__ == '__main__':
    main()
