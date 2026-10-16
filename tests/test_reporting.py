import asyncio
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from reporting.dashboards import definitions
from reporting.posthog import PostHog
from reporting.queries import EVENTS, interval, queries, report_metadata
from reporting.aggregate_safety import LEGACY_FIELDS, LEGACY_LIMITS, validate_rows
from reporting.setup_dashboards import create_dashboards, list_all


class QueryTests(unittest.TestCase):
    def test_explicit_periods_and_collection_warning(self):
        metadata = report_metadata(date(2026, 10, 10), 'Europe/Moscow')
        self.assertEqual(metadata['report_day'], '2026-10-09')
        self.assertEqual(metadata['previous_day'], '2026-10-08')
        self.assertEqual(metadata['periods']['report_day']['start'], '2026-10-08T21:00:00+00:00')
        self.assertEqual(metadata['periods']['baseline']['start'], '2026-10-01T21:00:00+00:00')
        self.assertEqual(metadata['periods']['baseline']['end_exclusive'], '2026-10-08T21:00:00+00:00')
        self.assertEqual(set(metadata['aggregate_periods']), set(queries(date(2026, 10, 10))))
        self.assertIn('debug_assumed', ' '.join(metadata['warnings']))
        self.assertIn('2026-10-09', ' '.join(metadata['warnings']))
        self.assertNotIn('Only explicitly captured consented', ' '.join(metadata['warnings']))

    def test_raw_columns_and_nonfinite_metrics_cannot_pass(self):
        row = {'day': '2026-10-09', 'event': 'model_selected', 'deliveries': 2,
               'events': 1, 'identities': 1}
        self.assertEqual(validate_rows([row], LEGACY_FIELDS['daily_events'], 400), [row])
        for key in ('distinct_id', 'session_id', 'flow_id', 'attempt_id', 'generation_id',
                    'prompt', 'search_query', 'error', 'account_id', 'task_id', 'url'):
            with self.assertRaises(ValueError):
                validate_rows([{**row, key: 'private-value'}], LEGACY_FIELDS['daily_events'], 400)
        for value in (float('nan'), float('inf'), -1, True, 'private-value'):
            with self.assertRaises(ValueError):
                validate_rows([{**row, 'events': value}], LEGACY_FIELDS['daily_events'], 400)

    def test_upstream_truncation_is_preserved(self):
        client = PostHog('https://posthog.example', 1, 'synthetic-token')
        with patch.object(client, 'request', return_value={
                'columns': ['n'], 'results': [[1]], 'hasMore': True}):
            self.assertTrue(client.query('SELECT count() AS n FROM events').truncated)

    def test_empty_result_with_wrong_columns_is_not_valid_coverage(self):
        client = PostHog('https://posthog.example',1,'synthetic-token')
        with patch.object(client,'request',return_value={'columns':['distinct_id'],'results':[]}):
            with self.assertRaises(ValueError):
                validate_rows(client.query('SELECT count() AS active_accounts'),LEGACY_FIELDS['account_users'],1)

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
    async def test_synthetic_ux_through_public_tool_and_independent_complete(self):
        from cryptography.fernet import Fernet
        from fastmcp import Client
        from fastmcp.server.auth import AccessToken
        from reporting.server import create_server
        from test_ux_reporting import AS_OF,full_path
        from ux_sqlite import SyntheticPostHog
        database = SyntheticPostHog(full_path())
        def query(sql):
            if sql.startswith('WITH periods AS') or 'raw_events' in sql:
                return database.query(sql)
            return []
        with tempfile.TemporaryDirectory() as directory:
            env = {'REPORT_POSTHOG_ORIGIN':'https://posthog.example','REPORT_PUBLIC_ORIGIN':'https://report.example',
                   'REPORT_PROJECT_ID':'1','REPORT_OAUTH_CLIENT_ID':'synthetic-client','REPORT_OAUTH_CLIENT_SECRET':'synthetic',
                   'REPORT_SIGNING_KEY':'x'*48,'REPORT_STORAGE_KEY':Fernet.generate_key().decode(),'REPORT_STATE_DIR':directory,
                   'REPORT_REDIRECT_URIS':'["https://chatgpt.com/connector_platform_oauth_redirect"]',
                   'REPORT_DASHBOARD_LINKS':'{"overview":"https://posthog.example/project/1/dashboard/2","journey":"https://posthog.example/project/1/dashboard/3"}'}
            async with Client(create_server(env)) as client:
                token=AccessToken(token='synthetic-token',client_id='synthetic',scopes=['query:read','project:read'])
                with patch('reporting.server.get_access_token',return_value=token), \
                     patch('reporting.server.datetime') as clock,patch('reporting.posthog.PostHog.query',side_effect=query):
                    clock.now.return_value=AS_OF
                    result=await client.call_tool('analytics_daily_report',{'report_day':'2026-10-09'})
                    self.assertTrue(result.data['complete'])
                    self.assertTrue(result.data['ux']['coverage']['complete'])
                    self.assertEqual(result.data['ux']['blocks']['journey']['rows']['journey'][0]['used'],1)
                    self.assertEqual(set(result.data['dashboards']),{'overview','journey','ux'})
                    def partial(sql):
                        if 'per_flow AS' in sql: raise RuntimeError('PRIVATE error')
                        return query(sql)
                    with patch('reporting.posthog.PostHog.query',side_effect=partial):
                        result=await client.call_tool('analytics_daily_report',{'report_day':'2026-10-09'})
                        self.assertTrue(result.data['complete'])
                        self.assertFalse(result.data['ux']['coverage']['complete'])
                        self.assertNotIn('PRIVATE',json.dumps(result.data))

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
                    self.assertTrue(all(value['status'] == 'unavailable'
                                        for value in data['query_coverage'].values()))
                with patch('reporting.server.get_access_token', return_value=token), \
                     patch('reporting.posthog.PostHog.query', return_value=[]):
                    result = await client.call_tool('analytics_daily_report', {})
                    self.assertTrue(result.data['complete'])
                    self.assertTrue(result.data['ux']['coverage']['complete'])
                    self.assertEqual(len(result.data['ux']['blocks']), 5)
                    self.assertTrue(all(block['status'] == 'available'
                                        for block in result.data['ux']['blocks'].values()))
                    self.assertEqual(result.data['ux']['coverage']['status'],'zero_observed')
                    self.assertTrue(all(value['status'] == 'available_empty'
                                        for value in result.data['query_coverage'].values()))
                links = await client.call_tool('analytics_dashboard_links', {})
                self.assertEqual(links.data['dashboards']['ux'],
                                 'https://posthog.example/project/1/dashboard/4')
                model = {'provider': 'synthetic', 'model_id': 'synthetic-model',
                         'event': 'generation_submitted', 'events': 1}
                with patch('reporting.server.get_access_token', return_value=token), \
                     patch('reporting.posthog.PostHog.query', side_effect=[[], [], [], [model] * 100, [], []]+[[]]*16):
                    result = await client.call_tool('analytics_daily_report', {})
                    self.assertTrue(result.data['complete'])
                    self.assertTrue(result.data['query_coverage']['models']['truncated'])
                with patch('reporting.server.get_access_token', return_value=token), \
                     patch('reporting.posthog.PostHog.query', side_effect=[
                         [{'day': '2026-10-09', 'event': 'model_selected', 'deliveries': 1,
                           'events': 1, 'identities': 1, 'distinct_id': 'private-identity'}],
                         [], [], [], [], []]+[[]]*16):
                    result = await client.call_tool('analytics_daily_report', {})
                    self.assertFalse(result.data['complete'])
                    self.assertEqual(set(result.data['errors']), {'daily_events'})
                    self.assertNotIn('private-identity', json.dumps(result.data))
                with patch('reporting.server.get_access_token', return_value=token), \
                     patch('reporting.posthog.PostHog.query', side_effect=RuntimeError('private raw SQL/token')):
                    result = await client.call_tool('analytics_daily_report', {})
                    self.assertNotIn('private raw SQL/token', json.dumps(result.data))
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
                self.assertFalse(response.json().get('client_id_metadata_document_supported', False))
                self.assertEqual(response.json()['registration_endpoint'], 'https://report.example/register')
                response = await client.post('/register', json={'redirect_uris': ['https://attacker.example/callback']})
                self.assertGreaterEqual(response.status_code, 400)
                response = await client.post('/register', json={
                    'client_name': 'Synthetic DCR test',
                    'redirect_uris': ['https://chatgpt.com/connector_platform_oauth_redirect'],
                    'grant_types': ['authorization_code', 'refresh_token'],
                    'token_endpoint_auth_method': 'none',
                    'scope': 'query:read project:read'})
                self.assertEqual(response.status_code, 201)
                registered = response.json()
                response = await client.get('/authorize', params={
                    'client_id': registered['client_id'], 'response_type': 'code',
                    'redirect_uri': 'https://chatgpt.com/connector_platform_oauth_redirect',
                    'scope': 'query:read project:read', 'state': 'synthetic-test',
                    'code_challenge': 'x' * 43, 'code_challenge_method': 'S256',
                    'resource': 'https://report.example/mcp'})
                self.assertEqual(response.status_code, 302)
                self.assertIn('/consent', response.headers['location'])
                response = await client.get(response.headers['location'])
                self.assertEqual(response.status_code, 200)
                self.assertNotIn('Client Not Registered', response.text)


if __name__ == '__main__':
    unittest.main()
