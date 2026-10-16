"""Validate aggregate output before it crosses the MCP boundary."""
import math
import re
from datetime import date, datetime

from reporting.queries import EVENTS


LEGACY_FIELDS = {
    'daily_events': {'day': 'day', 'event': 'event', 'deliveries': 'count',
                     'events': 'count', 'identities': 'count'},
    'daily_outcomes': {'day': 'day', 'outcome': 'outcome', 'events': 'count'},
    'daily_duration': {'day': 'day', 'samples': 'count', 'mean_ms': 'number',
                       'median_ms': 'number', 'p95_ms': 'number'},
    'models': {'provider': 'label', 'model_id': 'model', 'event': 'event', 'events': 'count'},
    'account_users': {'active_accounts': 'count'},
    'freshness': {'last_product_event': 'timestamp', 'product_deliveries': 'count'},
}
LEGACY_LIMITS = {'daily_events': 400, 'daily_outcomes': 160, 'daily_duration': 31,
                 'models': 100, 'account_users': 1, 'freshness': 1}


def validate_value(value, kind):
    if kind == 'flag':
        if value not in (0, 1, False, True):
            raise ValueError('Invalid aggregate flag')
        return int(value)
    if kind.startswith('enum:'):
        if not isinstance(value, str) or value not in kind[5:].split('|'):
            raise ValueError('Invalid aggregate category')
        return value
    if kind in ('count', 'number'):
        if value is None and kind == 'number':
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('Invalid aggregate value')
        if not math.isfinite(value) or value < 0 or (kind == 'count' and int(value) != value):
            raise ValueError('Invalid aggregate value')
        return value
    if kind == 'timestamp' and value is None:
        return None
    if not isinstance(value, str):
        raise ValueError('Invalid aggregate value')
    if kind == 'day':
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError('Invalid aggregate value')
    elif kind == 'timestamp':
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    elif kind == 'event':
        if value not in EVENTS:
            raise ValueError('Invalid aggregate value')
    elif kind == 'outcome':
        if value not in ('success', 'fail', 'cancelled', 'unknown'):
            raise ValueError('Invalid aggregate value')
    elif kind == 'label':
        # Catalog labels only: forbid free text, URLs and oversized payloads.
        if not re.fullmatch(r'[A-Za-z0-9_./:@+ -]{1,120}', value) or '://' in value:
            raise ValueError('Invalid aggregate value')
    elif kind == 'model':
        if not re.fullmatch(r'~?[A-Za-z0-9][A-Za-z0-9._:/-]{0,99}', value) or '..' in value or '://' in value:
            raise ValueError('Invalid model catalog ID')
    elif kind == 'version':
        if value != 'unknown' and not re.fullmatch(r'[0-9][A-Za-z0-9.+_-]{0,39}', value):
            raise ValueError('Invalid application version')
    else:
        raise ValueError('Unknown aggregate type')
    return value


def validate_rows(rows, fields, limit):
    if not isinstance(rows, list) or len(rows) > limit:
        raise ValueError('Invalid aggregate rows')
    columns = getattr(rows,'columns',None)
    if columns is not None and set(columns)!=set(fields):
        raise ValueError('Unexpected aggregate columns')
    clean = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(fields):
            raise ValueError('Unexpected aggregate columns')
        clean.append({key: (validate_parameter(row['parameter'], row[key]) if kind == 'parameter_value'
                            else '' if kind == 'optional_parameter_value' and row[key]==''
                            else validate_parameter(row['parameter'], row[key]) if kind == 'optional_parameter_value'
                            else validate_value(row[key], kind)) for key, kind in fields.items()})
    return clean


def validate_parameter(parameter, value):
    # Exact canonical parameter projection, not arbitrary JSON settings.
    if not isinstance(value, str):
        raise ValueError('Invalid parameter value')
    patterns = {
        'aspect_ratio': r'(auto|adaptive|original|square|portrait|landscape|[1-9]\d?:[1-9]\d?)',
        'reasoning': r'(none|minimal|low|medium|high|xhigh|max|ultra)',
        'speed': r'(standard|fast|TURBO|BALANCED|QUALITY)',
        'resolution': r'(auto|low|medium|high|standard|hd|sd|[1-9]\d{2,3}p?|(?:[1248]|1\.5)[kK]|[1-9]\d{2,3}x[1-9]\d{2,3})',
        'output_format': r'(png|jpg|jpeg|webp|mp4|mov|webm|mp3|wav|ogg|aac|flac|pcm|pcm16)',
    }
    if parameter == 'model_id':
        return validate_value(value, 'model')
    if parameter in ('duration', 'count'):
        if not re.fullmatch(r'\d+(\.\d+)?', value):
            raise ValueError('Invalid parameter value')
        number = float(value)
        if parameter == 'count' and not (1 <= number <= 100 and number.is_integer()):
            raise ValueError('Invalid parameter value')
        if parameter == 'duration' and not (0 <= number <= 3600):
            raise ValueError('Invalid parameter value')
    elif parameter not in patterns or not re.fullmatch(patterns[parameter], value):
        raise ValueError('Invalid parameter value')
    return value
