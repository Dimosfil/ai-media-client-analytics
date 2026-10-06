"""Read-only live verification; requires a private, scoped setup/read token."""
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from reporting.dashboards import definitions
from reporting.posthog import PostHog
from reporting.queries import queries


def main():
    client = PostHog(os.environ['REPORT_POSTHOG_ORIGIN'], os.environ['REPORT_PROJECT_ID'],
                     os.environ['REPORT_SETUP_TOKEN'])
    today = datetime.now(ZoneInfo('Europe/Moscow')).date()
    failures = []
    for name, sql in queries(today).items():
        try:
            rows = client.query(sql)
            print(json.dumps({'query': name, 'ok': True, 'rows': len(rows)}))
        except RuntimeError as exc:
            failures.append(name)
            print(json.dumps({'query': name, 'ok': False, 'error': str(exc)}))
    # Validate/execute every chart's source through the actual deployed schema.
    for dashboard in definitions():
        for insight in dashboard['insights']:
            try:
                result = client.request('POST', f'/api/projects/{client.project_id}/query/',
                    {'query': insight['query']['source'], 'refresh': 'force_blocking'})
                status = result.get('query_status') or {}
                if result.get('error') or status.get('error') or status.get('complete') is False or 'results' not in result:
                    raise RuntimeError('Chart did not return synchronous results')
                print(json.dumps({'chart': insight['key'], 'ok': True}))
            except RuntimeError as exc:
                failures.append(insight['key'])
                print(json.dumps({'chart': insight['key'], 'ok': False, 'error': str(exc)}))
    if failures:
        raise SystemExit('Unverified queries/charts: ' + ', '.join(failures))


if __name__ == '__main__':
    main()
