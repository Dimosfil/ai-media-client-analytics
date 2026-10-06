import json
import urllib.error
import urllib.request
from urllib.parse import urlparse


class PostHog:
    def __init__(self, origin, project_id, token, timeout=45):
        parsed = urlparse(origin)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
                or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/')):
            raise ValueError('PostHog origin must be an HTTPS origin without credentials or path')
        if int(project_id) < 1:
            raise ValueError('Invalid project ID')
        self.origin = origin.rstrip('/')
        self.project_id = int(project_id)
        self.token = token
        self.timeout = timeout

    def request(self, method, path, body=None):
        if not path.startswith('/api/') or path.startswith('//'):
            raise ValueError('Only PostHog API paths are supported')
        payload = None if body is None else json.dumps(body, ensure_ascii=False).encode('utf-8')
        request = urllib.request.Request(self.origin + path, data=payload, method=method,
            headers={'Authorization': f'Bearer {self.token}',
                     'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'})
        # Never follow redirects with Authorization to another origin.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        try:
            with urllib.request.build_opener(NoRedirect()).open(request, timeout=self.timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            # Upstream bodies can contain SQL, private data and credentials; do not log them.
            raise RuntimeError(f'PostHog API returned HTTP {exc.code}') from None
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError('PostHog API is unreachable or timed out') from None
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise RuntimeError('PostHog API returned invalid JSON') from None

    def query(self, sql):
        response = self.request('POST', f'/api/projects/{self.project_id}/query/',
            {'query': {'kind': 'HogQLQuery', 'query': sql}, 'refresh': 'force_blocking'})
        if not isinstance(response, dict):
            raise RuntimeError('Unexpected query response shape')
        status = response.get('query_status') or {}
        if response.get('error') or status.get('error') or status.get('complete') is False:
            raise RuntimeError('PostHog query failed')
        rows, columns = response.get('results'), response.get('columns')
        if not isinstance(rows, list) or not isinstance(columns, list):
            raise RuntimeError('PostHog did not return synchronous query results')
        if len(rows) > 400 or any(not isinstance(row, list) or len(row) != len(columns) for row in rows):
            raise RuntimeError('Unexpected query response shape')
        return [dict(zip(columns, row)) for row in rows]
