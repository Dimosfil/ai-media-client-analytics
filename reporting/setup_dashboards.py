"""Operator-only writer; the reporting MCP never imports or exposes this tool."""
import argparse
import json
import os
from urllib.parse import urlparse

from reporting.dashboards import MARKER, definitions
from reporting.posthog import PostHog


def list_all(client, path):
    results = []
    for _ in range(100):
        page = client.request('GET', path)
        if not isinstance(page, dict) or not isinstance(page.get('results'), list):
            raise RuntimeError('Unexpected PostHog collection response; refusing setup')
        results.extend(page.get('results', []))
        next_url = page.get('next')
        if not next_url:
            return results
        parsed = urlparse(next_url)
        if parsed.scheme + '://' + parsed.netloc != client.origin:
            raise RuntimeError('Pagination attempted to leave the PostHog origin')
        path = parsed.path + ('?' + parsed.query if parsed.query else '')
    raise RuntimeError('Pagination limit reached')


def create_dashboards(client, apply=False):
    base = f'/api/projects/{client.project_id}'
    existing_dashboards = list_all(client, base + '/dashboards/')
    existing_insights = list_all(client, base + '/insights/?saved=true')
    links = {}
    for definition in definitions():
        marker = f"{MARKER} dashboard={definition['key']}"
        matches = [d for d in existing_dashboards if (d.get('description') or '').startswith(marker)]
        if len(matches) > 1:
            raise RuntimeError('Duplicate managed dashboard markers; review before continuing')
        dashboard = matches[0] if matches else None
        if dashboard is None and apply:
            dashboard = client.request('POST', base + '/dashboards/', {
                'name': definition['name'], 'description': marker + '\n' + definition['description'],
                'pinned': True, 'is_shared': False})
        if dashboard:
            links[definition['key']] = f"{client.origin}/project/{client.project_id}/dashboard/{dashboard['id']}"
        for insight in definition['insights']:
            insight_marker = f"{MARKER} insight={insight['key']}"
            matches = [i for i in existing_insights if (i.get('description') or '').startswith(insight_marker)]
            if len(matches) > 1:
                raise RuntimeError('Duplicate managed insight markers; review before continuing')
            if matches:
                # Refuse to change a user's edited query or dashboard membership implicitly.
                if apply and dashboard['id'] not in matches[0].get('dashboards', []):
                    raise RuntimeError('Managed insight exists outside its dashboard; restore membership manually')
                continue
            if apply:
                client.request('POST', base + '/insights/', {'name': insight['name'],
                    'description': insight_marker + '\n' + insight['description'],
                    'query': insight['query'], 'saved': True, 'dashboards': [dashboard['id']]})
    return links


def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Create missing managed objects; never overwrite existing ones')
    args = parser.parse_args()
    if not args.apply:
        print(json.dumps(definitions(), ensure_ascii=False, indent=2))
        return
    client = PostHog(os.environ['REPORT_POSTHOG_ORIGIN'], os.environ['REPORT_PROJECT_ID'],
                     os.environ['REPORT_SETUP_TOKEN'])
    print(json.dumps(create_dashboards(client, apply=True), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
