import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from reporting.check import main
from reporting.posthog import QueryRows
from reporting.ux_contract import QueryPlan


class LiveCheckTests(unittest.TestCase):
    def run_check(self, argv, rows=None, failure=False):
        client = Mock()
        if failure:
            client.query.side_effect = RuntimeError('PostHog query failed')
        else:
            client.query.return_value = rows if rows is not None else QueryRows(
                [{'events': 1}, {'events': 2}], truncated=True, columns=['events'])
        output = io.StringIO()
        env = {'REPORT_POSTHOG_ORIGIN': 'https://analytics.example',
               'REPORT_PROJECT_ID': '1', 'REPORT_SETUP_TOKEN': 'synthetic-read-token'}
        with patch.dict('os.environ', env), patch('reporting.check.PostHog', return_value=client), \
                patch('reporting.check.queries', return_value={}), \
                patch('reporting.check.plans', return_value={'bounded': QueryPlan('SELECT 1', {'events': 'count'}, 2)}), \
                patch('reporting.check.definitions', return_value=[]), redirect_stdout(output):
            try:
                main(argv)
            finally:
                self.output = [json.loads(line) for line in output.getvalue().splitlines()]

    def test_truncation_fails_the_default_gate(self):
        with self.assertRaises(SystemExit):
            self.run_check([])
        self.assertFalse(self.output[0]['ok'])
        self.assertTrue(self.output[0]['truncated'])

    def test_explicit_bounded_gate_preserves_incomplete_status(self):
        self.run_check(['--allow-truncated'])
        self.assertTrue(self.output[0]['ok'])
        self.assertFalse(self.output[0]['complete'])
        self.assertTrue(self.output[0]['truncated'])

    def test_bounded_gate_does_not_hide_query_failures(self):
        with self.assertRaises(SystemExit):
            self.run_check(['--allow-truncated'], failure=True)
        self.assertFalse(self.output[0]['ok'])

    def test_bounded_gate_does_not_accept_raw_columns(self):
        rows = QueryRows([{'distinct_id': 'u_private'}], columns=['distinct_id'])
        with self.assertRaises(SystemExit):
            self.run_check(['--allow-truncated'], rows=rows)
        self.assertFalse(self.output[0]['ok'])
        self.assertNotIn('u_private', json.dumps(self.output))


if __name__ == '__main__':
    unittest.main()
