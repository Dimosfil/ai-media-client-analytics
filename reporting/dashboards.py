"""Managed PostHog insight definitions, independent of the deployment/project ID."""

MARKER = '[ai-media-analytics-report:v1]'


def event(name, math='total', outcome=None):
    node = {'kind': 'EventsNode', 'event': name, 'name': name, 'math': math}
    if outcome:
        node['properties'] = [{'key': 'outcome', 'value': outcome, 'operator': 'exact', 'type': 'event'}]
    return node


def viz(query):
    return {'kind': 'InsightVizNode', 'source': query}


def trends(series, extra=None):
    return viz({'kind': 'TrendsQuery', 'dateRange': {'date_from': '-30d'}, 'interval': 'day',
                'series': series, 'trendsFilter': {'display': 'ActionsLineGraph', **(extra or {})}})


def definitions():
    success = event('generation_completed', outcome='success')
    duration = {**success, 'math': 'p95', 'math_property': 'duration_ms'}
    retained = {'id': 'generation_completed', 'name': 'generation_completed',
                'type': 'events', 'properties': success['properties']}
    native_counts = 'PostHog native charts count captures; compare repeat deliveries with the daily report.'
    return [
        {'key': 'overview', 'name': 'AI Media Client — Product overview',
         'description': f'{MARKER} Explicit consented product events; live rolling 30 days. '
             'Smoke is excluded by named series. Counts are not financial accounting.',
         'insights': [
             {'key': 'activity', 'name': 'Активные идентичности по событиям',
              'description': 'Unique IDs per event/day; do not add visitor and account series as people.',
              'query': trends([event('landing_viewed', 'dau'), event('studio_opened', 'dau'),
                               event('generation_submitted', 'dau')])},
             {'key': 'jobs', 'name': 'Принятые и завершённые генерации',
              'description': 'Accepted and terminal events may be on different days. ' + native_counts,
              'query': trends([event('generation_submitted'), success,
                               event('generation_completed', outcome='fail'),
                               event('generation_completed', outcome='cancelled'),
                               event('generation_completed', outcome='unknown')])},
             {'key': 'success', 'name': 'Успешность среди success и fail',
              'description': '100 * success / (success + fail). Cancelled/unknown excluded; zero denominator is undefined.',
              'query': trends([success, event('generation_completed', outcome='fail')],
                               {'formula': '100 * A / (A + B)'})},
             {'key': 'duration', 'name': 'P95 длительности успешных генераций, мс',
              'description': 'Only delivered successful events with numeric duration_ms. Small samples are unstable.',
              'query': trends([duration])},
             {'key': 'models', 'name': 'Модели и провайдеры за 30 дней',
              'description': 'Deduplicated by event uuid. Missing provider/model_id remain unknown.',
              'query': {'kind': 'DataTableNode', 'source': {'kind': 'HogQLQuery', 'query':
                  "SELECT coalesce(toString(properties.provider), 'unknown') AS provider, "
                  "coalesce(toString(properties.model_id), 'unknown') AS model_id, event, uniqExact(uuid) AS events "
                  "FROM events WHERE timestamp >= now() - INTERVAL 30 DAY "
                  "AND event IN ('generation_submitted', 'generation_completed') "
                  "GROUP BY provider, model_id, event ORDER BY events DESC LIMIT 100"}}},
         ]},
        {'key': 'journey', 'name': 'AI Media Client — Funnels and retention',
         'description': f'{MARKER} Funnels compare matching identities only. Anonymous visitors and accounts '
             'are not automatically linked. Sparse/unmatured retention is not a product verdict.',
         'insights': [
             {'key': 'activation', 'name': 'Вход → принятие → успешная генерация',
              'description': 'Ordered account identity funnel with a 7-day conversion window.',
              'query': viz({'kind': 'FunnelsQuery', 'dateRange': {'date_from': '-30d'},
                  'series': [event('login_completed'), event('generation_submitted'), success],
                  'funnelsFilter': {'funnelWindowInterval': 7, 'funnelWindowIntervalUnit': 'day',
                                    'funnelOrderType': 'ordered'}})},
             {'key': 'choice', 'name': 'Выбор модели → цена → принятие',
              'description': 'Same-identity selection funnel. Missing instrumentation must not be called drop-off.',
              'query': viz({'kind': 'FunnelsQuery', 'dateRange': {'date_from': '-30d'},
                  'series': [event('model_selected'), event('quote_shown'), event('generation_submitted')],
                  'funnelsFilter': {'funnelWindowInterval': 1, 'funnelWindowIntervalUnit': 'day',
                                    'funnelOrderType': 'ordered'}})},
             {'key': 'retention', 'name': 'Возврат к успешной генерации D0–D7',
              'description': 'First successful generation cohort; compare only mature cohorts and show cohort size.',
              'query': viz({'kind': 'RetentionQuery', 'dateRange': {'date_from': '-30d'},
                  'retentionFilter': {'retentionType': 'retention_first_time', 'period': 'Day',
                      'totalIntervals': 8, 'targetEntity': retained, 'returningEntity': retained}})},
         ]},
    ]
