import asyncio
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from reporting.dashboards import definitions
from reporting.posthog import PostHog
from reporting.queries import EVENTS, interval, queries
from reporting.setup_dashboards import create_dashboards, list_all


class QueryTests(unittest.TestCase):
    def test_moscow_calendar_midnight(self):
        start, end = interval(date(2026, 10, 7), 1, 'Europe/Moscow')
        self.assertEqual(start.isoformat(), '2026-10-05T21:00:00+00:00')
        self.assertEqual(end.isoformat(), '2026-10-06T21:00:00+00:00')

    def test_boundaries_and_allowlisted_events(self):
        with self.assertRaises(ValueError):
            interval(date.today(), 100, 'Europe/Moscow')
        with self.assertRaises(ValueError):
            queries(date.today(), zone="UTC'); DROP TABLE events;")
        self.assertNotIn('analytics_smoke', EVENTS)
        for sql in queries(date(2026, 10, 7)).values():
            self.assertTrue(sql.startswith('SELECT '))
            self.assertNotIn('SELECT *', sql)
            self.assertNotIn('person.properties', sql)

    def test_origin_credentials_are_rejected(self):
        for origin in ['http://posthog.example', 'https://user:pass@posthog.example',
                       'https://posthog.example/api', 'https://posthog.example?token=secret']:
            with self.assertRaises(ValueError):
                PostHog(origin, 1, '')

    def test_pending_or_wrong_shape_is_not_zero(self):
        client = PostHog('https://posthog.example', 1, 'not-a-real-token')
        with patch.object(client, 'request', return_value={'query_status': {'complete': False}}):
            with self.assertRaises(RuntimeError):
                client.query('SELECT 1')
        with patch.object(client, 'request', return_value={'columns': ['n'], 'results': [[1, 2]]}):
            with self.assertRaises(RuntimeError):
                client.query('SELECT 1')

    def test_no_cross_origin_pagination(self):
        client = PostHog('https://posthog.example', 1, 'not-a-real-token')
        with patch.object(client, 'request', return_value={'results': [], 'next': 'https://attacker.example/api/'}):
            with self.assertRaises(RuntimeError):
                list_all(client, '/api/projects/1/insights/')


class SetupTests(unittest.TestCase):
    def test_repeat_setup_does_not_write_or_overwrite(self):
        from reporting.dashboards import MARKER
        dashboards, insights = [], []
        for index, dashboard in enumerate(definitions(), 1):
            dashboards.append({'id': index, 'description': f"{MARKER} dashboard={dashboard['key']}"})
            for insight in dashboard['insights']:
                insights.append({'description': f"{MARKER} insight={insight['key']}", 'dashboards': [index]})
        client = PostHog('https://posthog.example', 1, 'not-a-real-token')
        with patch.object(client, 'request', side_effect=[{'results': dashboards}, {'results': insights}]) as request:
            links = create_dashboards(client, apply=True)
            self.assertEqual(len(links), 2)
            self.assertTrue(all(call.args[0] == 'GET' for call in request.call_args_list))


class MCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_fixed_tools_and_failure_visibility(self):
        from cryptography.fernet import Fernet
        from fastmcp import Client
        from fastmcp.server.auth import AccessToken
        from reporting.server import create_server
        with tempfile.TemporaryDirectory() as directory:
            env = {'REPORT_POSTHOG_ORIGIN': 'https://posthog.example', 'REPORT_PUBLIC_ORIGIN': 'https://report.example',
                   'REPORT_PROJECT_ID': '1', 'REPORT_OAUTH_CLIENT_ID': 'synthetic-client',
                   'REPORT_OAUTH_CLIENT_SECRET': 'synthetic-client-secret', 'REPORT_SIGNING_KEY': 'x' * 48,
                   'REPORT_STORAGE_KEY': Fernet.generate_key().decode(), 'REPORT_STATE_DIR': directory,
                   'REPORT_REDIRECT_URIS': '["https://chatgpt.com/connector_platform_oauth_redirect"]'}
            server = create_server(env)
            async with Client(server) as client:
                tools = await client.list_tools()
                self.assertEqual({tool.name for tool in tools}, {'analytics_daily_report', 'analytics_dashboard_links'})
                report_tool = next(tool for tool in tools if tool.name == 'analytics_daily_report')
                self.assertEqual(set(report_tool.input_schema['properties']), {'report_day'})
                self.assertTrue(report_tool.annotations.read_only_hint)
                token = AccessToken(token='synthetic-opaque-token', client_id='synthetic-client', scopes=['query:read', 'project:read'])
                with patch('reporting.server.get_access_token', return_value=token), \
                     patch('reporting.posthog.PostHog.query', side_effect=RuntimeError('PostHog API returned HTTP 503')):
                    result = await client.call_tool('analytics_daily_report', {})
                    data = result.data
                    self.assertFalse(data['complete'])
                    self.assertEqual(len(data['errors']), 6)
                    self.assertEqual(data['data'], {})
                with patch('reporting.server.get_access_token', return_value=None):
                    with self.assertRaises(Exception):
                        await client.call_tool('analytics_daily_report', {})

    async def test_http_requires_oauth_and_exposes_discovery(self):
        import httpx2
        from cryptography.fernet import Fernet
        from reporting.server import create_server
        with tempfile.TemporaryDirectory() as directory:
            env = {'REPORT_POSTHOG_ORIGIN': 'https://posthog.example', 'REPORT_PUBLIC_ORIGIN': 'https://report.example',
                   'REPORT_PROJECT_ID': '1', 'REPORT_OAUTH_CLIENT_ID': 'synthetic-client',
                   'REPORT_OAUTH_CLIENT_SECRET': 'synthetic-secret', 'REPORT_SIGNING_KEY': 'x' * 48,
                   'REPORT_STORAGE_KEY': Fernet.generate_key().decode(), 'REPORT_STATE_DIR': directory,
                   'REPORT_REDIRECT_URIS': '["https://chatgpt.com/connector_platform_oauth_redirect"]'}
            app = create_server(env).http_app()
            async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url='https://report.example') as client:
                response = await client.post('/mcp', json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'})
                self.assertEqual(response.status_code, 401)
                self.assertIn('resource_metadata', response.headers['www-authenticate'])
                response = await client.get('/.well-known/oauth-authorization-server')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(set(response.json()['scopes_supported']), {'query:read', 'project:read'})
                response = await client.post('/register', json={'redirect_uris': ['https://attacker.example/callback']})
                self.assertGreaterEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
