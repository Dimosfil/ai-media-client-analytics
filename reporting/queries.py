"""No caller-supplied SQL, identities, property names or project IDs."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

EVENTS = (
    'landing_viewed', 'studio_opened', 'login_clicked', 'login_started',
    'login_completed', 'model_selected', 'quote_shown', 'generation_submitted',
    'generation_completed', 'purchase_fulfilled',
)


def interval(end_day: date, days: int, zone: str):
    if not 1 <= days <= 31:
        raise ValueError('days must be between 1 and 31')
    tz = ZoneInfo(zone)
    start = datetime.combine(end_day - timedelta(days=days), time.min, tz)
    end = datetime.combine(end_day, time.min, tz)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def queries(end_day: date, days: int = 8, zone: str = 'Europe/Moscow'):
    # zone is server configuration, not an MCP tool parameter.
    if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/_+-0123456789' for c in zone):
        raise ValueError('Invalid timezone')
    ZoneInfo(zone)
    start, end = interval(end_day, days, zone)
    where = (f"timestamp >= toDateTime('{start:%Y-%m-%d %H:%M:%S}', 'UTC') "
             f"AND timestamp < toDateTime('{end:%Y-%m-%d %H:%M:%S}', 'UTC')")
    day = f"toDate(toTimeZone(timestamp, '{zone}'))"
    catalog = ', '.join(repr(event) for event in EVENTS)
    return {
        'daily_events': f"SELECT {day} AS day, event, count() AS deliveries, "
            f"uniqExact(uuid) AS events, uniqExact(distinct_id) AS identities "
            f"FROM events WHERE {where} AND event IN ({catalog}) "
            "GROUP BY day, event ORDER BY day, event LIMIT 400",
        'daily_outcomes': f"SELECT {day} AS day, coalesce(toString(properties.outcome), 'unknown') AS outcome, "
            f"uniqExact(uuid) AS events FROM events WHERE {where} AND event = 'generation_completed' "
            "GROUP BY day, outcome ORDER BY day, outcome LIMIT 160",
        'daily_duration': f"SELECT {day} AS day, count() AS samples, "
            "avg(toFloat(properties.duration_ms)) AS mean_ms, "
            "quantile(0.5)(toFloat(properties.duration_ms)) AS median_ms, "
            "quantile(0.95)(toFloat(properties.duration_ms)) AS p95_ms "
            f"FROM events WHERE {where} AND event = 'generation_completed' "
            "AND properties.outcome = 'success' AND toFloat(properties.duration_ms) >= 0 "
            "GROUP BY day ORDER BY day LIMIT 31",
        'models': "SELECT coalesce(toString(properties.provider), 'unknown') AS provider, "
            "coalesce(toString(properties.model_id), 'unknown') AS model_id, "
            "event, uniqExact(uuid) AS events "
            f"FROM events WHERE {where} AND event IN ('generation_submitted', 'generation_completed') "
            "GROUP BY provider, model_id, event ORDER BY events DESC LIMIT 100",
        'account_users': "SELECT uniqExact(distinct_id) AS active_accounts "
            f"FROM events WHERE {where} AND startsWith(distinct_id, 'u_') AND event IN ({catalog})",
        'freshness': "SELECT max(timestamp) AS last_product_event, count() AS product_deliveries "
            f"FROM events WHERE timestamp >= toDateTime('{start:%Y-%m-%d %H:%M:%S}', 'UTC') "
            f"AND event IN ({catalog}) LIMIT 1",
    }


def report_metadata(end_day: date, zone: str):
    def period(end, days):
        start, stop = interval(end, days, zone)
        return {'start': start.isoformat(), 'end_exclusive': stop.isoformat(),
                'timezone': zone, 'days': days}

    periods = {'report_day': period(end_day, 1),
               'previous_day': period(end_day - timedelta(days=1), 1),
               'baseline': period(end_day - timedelta(days=1), 7),
               'legacy_window': period(end_day, 8)}
    daily_periods = {'row_period_key': 'day', 'periods': {
        (end_day - timedelta(days=offset)).isoformat(): period(end_day - timedelta(days=offset - 1), 1)
        for offset in range(1, 9)}}
    return {
        'timezone': zone,
        'report_day': (end_day - timedelta(days=1)).isoformat(),
        'previous_day': (end_day - timedelta(days=2)).isoformat(),
        'baseline_days': 7,
        'periods': periods,
        'aggregate_periods': {
            'daily_events': daily_periods,
            'daily_outcomes': daily_periods,
            'daily_duration': daily_periods,
            'models': periods['legacy_window'],
            'account_users': periods['legacy_window'],
            'freshness': {'start': periods['legacy_window']['start'],
                          'end_exclusive': 'query execution time', 'timezone': zone},
        },
        'legacy_population': 'all delivered catalog events; schema versions and UI/release populations are mixed',
        'warnings': [
            'Capture depends on collection_mode: consented capture and debug_assumed bypass must be distinguished.',
            'Coverage changed on 2026-10-09: debug builds began capture without confirmation; more capture does not prove more usage.',
            'Legacy aggregates mix schema v1/v2 and populations; use separate schema-v2 UX samples for product conclusions.',
            'The five main UX dashboard reports filter user/release; absence there does not prove debug/admin inactivity.',
            'Visitor v_ and account u_ identities are separate; do not sum them as people.',
            'Daily active identities cannot be added to obtain weekly active identities.',
            'Submitted and completed jobs can fall on different days.',
            'Success rate = success / (success + fail); report cancelled and unknown separately.',
            'Missing events do not prove inactivity; check capture freshness and event coverage.',
            'Percentiles use delivered duration samples; duplicates can bias them.',
            'Small samples are descriptive, not evidence of causation.',
            'Revenue and credits require reconciliation with application PostgreSQL.',
        ],
    }
