"""Fixed HogQL aggregates; identifiers never leave the final aggregation."""
from datetime import timedelta
import re

from reporting.queries import interval
from reporting.ux_contract import (ACTIONS, BASE_FIELDS, CONTROLS, CONTROL_ACTIONS, EVENTS, FAMILIES,
    KNOWN_PROPERTIES, OBSERVATION_HOURS, ORIGINS, PARAMETERS, QueryPlan, REASONS, SECTIONS, SESSION_HOURS,
    TECHNICAL, USE_ACTIONS, enum)


def literals(values):
    return ', '.join(repr(value) for value in values)


def instant(value):
    return f"toDateTime('{value:%Y-%m-%d %H:%M:%S}', 'UTC')"


def missing(key):
    return f"coalesce(toString(properties.{key}), '') = ''"


def dimension(key, values):
    return f"CASE WHEN toString(properties.{key}) IN ({literals(values)}) THEN toString(properties.{key}) ELSE 'unknown' END"


def sample_sql():
    return ("CASE " + ' '.join(f"WHEN properties.ui_mode = '{mode}' AND properties.release_channel = '{channel}' "
            f"THEN '{mode}_{channel}'" for mode in ('user', 'admin', 'admin_preview') for channel in ('release', 'debug'))
            + " ELSE 'unknown_population' END")


def family_sql():
    return 'CASE ' + ' '.join(f"WHEN event IN ({literals(events)}) THEN '{family}'"
                              for family, events in FAMILIES.items()) + " ELSE 'unknown' END"


def version_sql():
    return "CASE WHEN match(toString(properties.app_version), '^[0-9][A-Za-z0-9.+_-]{0,39}$') THEN toString(properties.app_version) ELSE 'unknown' END"


def model_sql(key):
    # The live HogQL parser rejects the compound regex guard after JSON CASE
    # expansion. LIKE preserves the URL/path-traversal exclusions.
    return (f"CASE WHEN match(toString(properties.{key}), '^~?[A-Za-z0-9][A-Za-z0-9._:/-]{{0,99}}$') "
            f"AND toString(properties.{key}) NOT LIKE '%://%' AND toString(properties.{key}) NOT LIKE '%..%' "
            f"THEN toString(properties.{key}) ELSE 'unknown' END")


def render(sql):
    # Aggregate JSON aliases are ordinary strings in HogQL, not events.properties.
    # Explicit JSON functions also preserve numeric/boolean versus string values.
    def replace(match):
        alias, column, path = match.groups()
        if alias == 'raw':
            return match.group(0)
        payload = {'clicked_properties':'clicked_payload','accepted_payload':'accepted_payload'}.get(column,'payload')
        reference = f'{alias}.{payload}' if alias else payload
        keys = ','.join(repr(key) for key in path[1:].split('.'))
        return (f"CASE WHEN JSONType({reference},{keys})='String' THEN JSONExtractString({reference},{keys}) "
                f"ELSE JSONExtractRaw({reference},{keys}) END")
    return re.sub(r'(?:(\w+)\.)?(properties|clicked_properties|accepted_payload)((?:\.[A-Za-z_$][A-Za-z0-9_$]*)+)',replace,sql)


def plans(end_day, as_of, zone='Europe/Moscow'):
    start, report_end = interval(end_day, 8, zone)
    observed_end = min(as_of, report_end + timedelta(hours=OBSERVATION_HOURS))
    periods = [('report_day', *interval(end_day, 1, zone)),
               ('previous_day', *interval(end_day - timedelta(days=1), 1, zone)),
               ('baseline', *interval(end_day - timedelta(days=1), 7, zone))]
    p = ' UNION ALL '.join(f"SELECT '{name}' AS period, {instant(a)} AS period_start, {instant(b)} AS period_end" for name, a, b in periods)
    # Deduplicate UUID deliveries before timing, count and relationship calculations.
    common = f"""WITH periods AS ({p}), deduplicated AS (
        SELECT raw.uuid AS uuid, raw.distinct_id AS distinct_id, any(raw.event) AS event, min(raw.timestamp) AS timestamp,
          argMin(raw.properties, raw.timestamp) AS payload, count() AS deliveries
        FROM events raw WHERE raw.timestamp >= {instant(start)} AND raw.timestamp < {instant(observed_end)}
          AND toString(raw.properties.schema_version) = '2' AND raw.event IN ({literals(EVENTS)})
          AND startsWith(raw.distinct_id, 'u_') GROUP BY raw.uuid, raw.distinct_id), e AS (
        SELECT uuid, distinct_id, event, timestamp, payload, deliveries,
          {sample_sql()} AS sample, {family_sql()} AS family,
          {version_sql()} AS app_version, {dimension('viewport_class', ('mobile','medium','wide'))} AS viewport_class
        FROM deduplicated)"""
    # HogQL/ClickHouse joins use equality keys; period membership is a WHERE filter.
    join_period = 'CROSS JOIN periods p'
    in_period = 'e.timestamp >= p.period_start AND e.timestamp < p.period_end'
    result = {}
    totals_fields = {'period': BASE_FIELDS['period'], 'sample': BASE_FIELDS['sample'],
                     'family': enum((*FAMILIES, 'all')), 'events': 'count', 'identities': 'count', 'deliveries': 'count'}
    totals = f"SELECT p.period, e.sample, e.family, count() AS events, uniqExact(e.distinct_id) AS identities, sum(e.deliveries) AS deliveries FROM e {join_period} WHERE {in_period} GROUP BY p.period,e.sample,e.family"
    all_totals = f"SELECT p.period, e.sample, 'all' AS family, count() AS events, uniqExact(e.distinct_id) AS identities, sum(e.deliveries) AS deliveries FROM e {join_period} WHERE {in_period} GROUP BY p.period,e.sample"
    result['totals'] = QueryPlan(common + ' ' + totals + ' UNION ALL ' + all_totals + ' LIMIT 400', totals_fields)

    dims = {
        'section': dimension('section', SECTIONS), 'from_section': dimension('from_section', SECTIONS),
        'to_section': dimension('to_section', SECTIONS), 'menu': dimension('menu', ('account','notifications','context','mobile','settings')),
        'control': dimension('control', CONTROLS), 'click_region': dimension('click_region', ('navigation','account','notifications','settings','model_picker','parameters','queue','result','sources','composer','other')),
        'element_type': dimension('element_type', ('button','link','input','select','summary')),
        'mode': dimension('mode', ('text','image','video','audio')),
        'provider': dimension('provider', ('kie','codex','routerai','apimart')),
        'model_id': model_sql('model_id'), 'selected_model_id': model_sql('selected_model_id'),
        'routing_mode': dimension('routing_mode', ('auto','direct')), 'origin': dimension('origin', ORIGINS),
        'draft_source': dimension('draft_source', ORIGINS), 'action': dimension('action', ACTIONS),
        'outcome': dimension('outcome', ('started','succeeded','failed','cancelled','success','fail','blocked','unknown','unconfirmed')),
        'scope': dimension('scope', ('chats','projects','archive','models','history')),
        'entity': dimension('entity', ('chat','project','record')), 'reason': dimension('reason', REASONS),
    }
    dims_fields = {
        'section': enum(SECTIONS), 'from_section': enum(SECTIONS), 'to_section': enum(SECTIONS),
        'menu': enum(('account','notifications','context','mobile','settings')), 'control': enum(CONTROLS),
        'click_region': enum(('navigation','account','notifications','settings','model_picker','parameters','queue','result','sources','composer','other')),
        'element_type': enum(('button','link','input','select','summary')), 'mode': enum(('text','image','video','audio')),
        'provider': enum(('kie','codex','routerai','apimart')), 'model_id': 'model', 'selected_model_id': 'model',
        'routing_mode': enum(('auto','direct')), 'origin': enum(ORIGINS), 'draft_source': enum(ORIGINS),
        'action': enum(ACTIONS), 'outcome': enum(('started','succeeded','failed','cancelled','success','fail','blocked','unknown','unconfirmed')),
        'scope': enum(('chats','projects','archive','models','history')), 'entity': enum(('chat','project','record')), 'reason': enum(REASONS),
    }
    groups = {
        'navigation_events': ('navigation', ('section','from_section','to_section','menu','control','click_region','element_type')),
        'configuration_events': ('configuration', ('mode','model_id','selected_model_id','routing_mode','origin')),
        'preparation_events': ('preparation', ('section','draft_source','reason')),
        'organization_events': ('organization', ('action','outcome','scope','entity')),
        'account_queue_events': ('account_queue', ('action','outcome')),
        'obstacle_events': ('obstacles', ('reason',)),
        'result_events': ('results', ('action','outcome','mode')),
        'server_events': ('server', ('mode','provider','model_id','selected_model_id','routing_mode','outcome')),
    }
    for name, (family, keys) in groups.items():
        # Server kind is the contract's mode field; do not invent properties.mode there.
        expressions = {key: dims[key] for key in keys}
        if family == 'server':
            expressions['mode'] = dimension('kind', ('text','image','video','audio'))
        fields = {**BASE_FIELDS, 'event': enum(EVENTS), **{key: dims_fields[key] for key in keys},
                  'events': 'count', 'identities': 'count', 'deliveries': 'count',
                  'empty_search': 'count', 'search_samples': 'count', 'no_selection': 'count',
                  'selection_samples': 'count', 'duration_samples': 'count', 'mean_duration_ms': 'number',
                  'ready_samples': 'count', 'mean_load_ms': 'number'}
        columns = ', '.join(f'{value} AS {key}' for key, value in expressions.items())
        group = 'p.period,e.sample,e.app_version,e.viewport_class,e.event,' + ','.join(keys)
        search = "e.event IN ('search_used','model_search_used') AND toFloat(e.properties.result_count) >= 0"
        selection = "e.event = 'model_picker_closed' AND toString(e.properties.selection_made) IN ('true','false')"
        duration = "e.event = 'model_picker_closed' AND toFloat(e.properties.duration_ms) >= 0"
        ready = "e.event = 'screen_ready' AND toFloat(e.properties.load_time_ms) >= 0"
        sql = f""" SELECT p.period,e.sample,e.app_version,e.viewport_class,e.event,{columns},
          count() AS events,uniqExact(e.distinct_id) AS identities,sum(e.deliveries) AS deliveries,
          countIf({search} AND toFloat(e.properties.result_count)=0) AS empty_search,countIf({search}) AS search_samples,
          countIf({selection} AND toString(e.properties.selection_made)='false') AS no_selection,countIf({selection}) AS selection_samples,
          countIf({duration}) AS duration_samples,sumIf(toFloat(e.properties.duration_ms),{duration})/nullIf(countIf({duration}),0) AS mean_duration_ms,
          countIf({ready}) AS ready_samples,sumIf(toFloat(e.properties.load_time_ms),{ready})/nullIf(countIf({ready}),0) AS mean_load_ms
          FROM e {join_period} WHERE {in_period} AND e.family='{family}' GROUP BY {group} ORDER BY events DESC LIMIT 400"""
        result[name] = QueryPlan(common + sql, fields)
    result.update(connected_plans(common, as_of))
    result['parameters'] = parameter_plan(common, in_period, join_period)
    result['parameter_comparison'] = comparison_plan(common, in_period, join_period)
    result['coverage'] = coverage_plan(start, report_end, as_of)
    return {name:QueryPlan(render(plan.sql),plan.fields,plan.limit) for name,plan in result.items()}


def connected_plans(common, as_of):
    """Temporal joins use observed prefixes, never independent daily ratios."""
    result = {}
    key = 'distinct_id,sample,flow_id'
    horizon = f"dateDiff('second', f.started_at, e.timestamp) >= 0 AND dateDiff('second', f.started_at, e.timestamp) < {OBSERVATION_HOURS*3600}"
    flow_columns = 'f.distinct_id,f.sample,f.flow_id,f.started_at,f.app_version,f.viewport_class'
    use = f"e.event='result_action' AND e.properties.action IN ({literals(USE_ACTIONS)}) AND e.properties.outcome='succeeded'"
    intent = "e.event='result_action' AND e.properties.action='download' AND e.properties.outcome='started'"
    flow_ctes = f""", flows AS (
      SELECT distinct_id,sample,toString(properties.flow_id) AS flow_id,min(timestamp) AS started_at,
        argMin(app_version,timestamp) AS app_version,argMin(viewport_class,timestamp) AS viewport_class
      FROM e WHERE event='composer_started' AND NOT ({missing('flow_id')}) GROUP BY distinct_id,sample,flow_id),
    attempts AS (
      SELECT {flow_columns},toString(e.properties.attempt_id) AS attempt_id,min(e.timestamp) AS clicked_at
      FROM flows f INNER JOIN e ON f.distinct_id=e.distinct_id AND f.sample=e.sample AND f.flow_id=toString(e.properties.flow_id)
      WHERE e.event='generation_submit_clicked' AND NOT ({missing('attempt_id')}) AND {horizon}
      GROUP BY {flow_columns},attempt_id),
    accepted AS (
      SELECT a.distinct_id,a.sample,a.flow_id,a.started_at,a.attempt_id,toString(e.properties.generation_id) AS generation_id,min(e.timestamp) AS accepted_at
      FROM attempts a INNER JOIN e ON a.distinct_id=e.distinct_id AND a.sample=e.sample AND a.flow_id=toString(e.properties.flow_id)
        AND a.attempt_id=toString(e.properties.attempt_id)
      WHERE e.event='generation_submitted' AND NOT ({missing('generation_id')}) AND e.timestamp>=a.clicked_at
        AND dateDiff('second',a.started_at,e.timestamp)<{OBSERVATION_HOURS*3600}
      GROUP BY a.distinct_id,a.sample,a.flow_id,a.started_at,a.attempt_id,generation_id),
    successes AS (
      SELECT j.distinct_id,j.sample,j.flow_id,j.started_at,j.attempt_id,j.generation_id,j.accepted_at,
        countIf(e.event='generation_completed' AND e.properties.outcome='success' AND e.timestamp>=j.accepted_at
          AND dateDiff('second',j.started_at,e.timestamp)<{OBSERVATION_HOURS*3600})>0 AS successful,
        minIf(e.timestamp,e.event='generation_completed' AND e.properties.outcome='success' AND e.timestamp>=j.accepted_at
          AND dateDiff('second',j.started_at,e.timestamp)<{OBSERVATION_HOURS*3600}) AS success_at
      FROM accepted j LEFT JOIN e ON j.distinct_id=e.distinct_id AND j.sample=e.sample AND j.generation_id=toString(e.properties.generation_id)
      GROUP BY j.distinct_id,j.sample,j.flow_id,j.started_at,j.attempt_id,j.generation_id,j.accepted_at),
    views AS (
      SELECT j.distinct_id,j.sample,j.flow_id,j.started_at,j.attempt_id,j.generation_id,j.successful,
        countIf(j.successful AND e.event='result_viewed' AND e.timestamp>=j.success_at
          AND dateDiff('second',j.started_at,e.timestamp)<{OBSERVATION_HOURS*3600})>0 AS viewed,
        minIf(e.timestamp,j.successful AND e.event='result_viewed' AND e.timestamp>=j.success_at
          AND dateDiff('second',j.started_at,e.timestamp)<{OBSERVATION_HOURS*3600}) AS viewed_at
      FROM successes j LEFT JOIN e ON j.distinct_id=e.distinct_id AND j.sample=e.sample AND j.generation_id=toString(e.properties.generation_id)
      GROUP BY j.distinct_id,j.sample,j.flow_id,j.started_at,j.attempt_id,j.generation_id,j.successful),
    uses AS (
      SELECT j.distinct_id,j.sample,j.flow_id,j.generation_id,j.successful,j.viewed,
        countIf(j.viewed AND {use} AND e.timestamp>=j.viewed_at AND dateDiff('second',j.started_at,e.timestamp)<{OBSERVATION_HOURS*3600})>0 AS used,
        countIf(j.viewed AND {intent} AND e.timestamp>=j.viewed_at AND dateDiff('second',j.started_at,e.timestamp)<{OBSERVATION_HOURS*3600})>0 AS download_intent
      FROM views j LEFT JOIN e ON j.distinct_id=e.distinct_id AND j.sample=e.sample AND j.generation_id=toString(e.properties.generation_id)
      GROUP BY j.distinct_id,j.sample,j.flow_id,j.generation_id,j.successful,j.viewed),
    attempt_counts AS (SELECT {key},count() AS attempts FROM attempts GROUP BY {key}),
    technical_flows AS (
      SELECT f.distinct_id,f.sample,f.flow_id,countIf(e.event='ui_obstacle_seen' AND e.properties.reason IN ({literals(TECHNICAL)}) AND {horizon})>0 AS technical
      FROM flows f LEFT JOIN e ON f.distinct_id=e.distinct_id AND f.sample=e.sample AND f.flow_id=toString(e.properties.flow_id)
      GROUP BY f.distinct_id,f.sample,f.flow_id),
    per_flow AS (
      SELECT {flow_columns},t.technical,max(coalesce(a.attempts,0)) AS attempts,
        countIf(j.generation_id IS NOT NULL AND j.generation_id!='')>0 AS accepted,
        max(coalesce(j.successful,0)) AS successful,max(coalesce(j.viewed,0)) AS viewed,max(coalesce(j.used,0)) AS used,
        max(coalesce(j.download_intent,0)) AS download_intent
      FROM flows f LEFT JOIN uses j ON f.distinct_id=j.distinct_id AND f.sample=j.sample AND f.flow_id=j.flow_id
      LEFT JOIN attempt_counts a ON f.distinct_id=a.distinct_id AND f.sample=a.sample AND f.flow_id=a.flow_id
      LEFT JOIN technical_flows t ON f.distinct_id=t.distinct_id AND f.sample=t.sample AND f.flow_id=t.flow_id
      GROUP BY {flow_columns},t.technical)"""
    maturity = f"dateDiff('second',f.started_at,{instant(as_of)}) >= {OBSERVATION_HOURS*3600}"
    fields = {**BASE_FIELDS, 'technical': 'flag', 'preparations': 'count', 'identities': 'count',
              'attempt_count': 'count', 'mature_preparations': 'count'}
    counts = []
    for name, cond in {'attempted': 'f.attempts>0', 'accepted': 'f.accepted>0', 'successful': 'f.successful>0',
                       'viewed': 'f.viewed>0', 'used': 'f.used>0', 'download_intent': 'f.download_intent>0'}.items():
        counts += [f'countIf({cond}) AS {name}', f'uniqExactIf(f.distinct_id,{cond}) AS {name}_identities',
                   f'countIf({maturity} AND {cond}) AS mature_{name}']
        fields.update({name: 'count', name+'_identities': 'count', 'mature_'+name: 'count'})
    sql = f""" SELECT p.period,f.sample,f.app_version,f.viewport_class,f.technical,count() AS preparations,
      uniqExact(f.distinct_id) AS identities,sum(f.attempts) AS attempt_count,countIf({maturity}) AS mature_preparations,{','.join(counts)}
      FROM per_flow f CROSS JOIN periods p WHERE f.started_at>=p.period_start AND f.started_at<p.period_end
      GROUP BY p.period,f.sample,f.app_version,f.viewport_class,f.technical ORDER BY preparations DESC LIMIT 400"""
    result['journey'] = QueryPlan(common + flow_ctes + sql, fields)
    result['discovery'] = discovery_plan(common, as_of)
    result['recovery'] = recovery_plan(common, as_of)
    result['successful_results'] = results_plan(common, as_of)
    return result


def discovery_plan(common, as_of):
    action = 'CASE ' + ' '.join(f"WHEN ({predicate}) THEN '{control}'" for control, predicate in CONTROL_ACTIONS.items()) + " ELSE 'unknown' END"
    ctes = f""", exposures AS (
      SELECT distinct_id,sample,toString(properties.$session_id) AS session_id,toString(properties.control) AS control,
        min(timestamp) AS seen_at,argMin(app_version,timestamp) AS app_version,argMin(viewport_class,timestamp) AS viewport_class
      FROM e WHERE event='control_viewed' AND NOT ({missing('$session_id')}) AND properties.control IN ({literals(CONTROL_ACTIONS)})
      GROUP BY distinct_id,sample,session_id,control), actions AS (
      SELECT distinct_id,sample,toString(properties.$session_id) AS session_id,timestamp,{action} AS control FROM e), linked AS (
      SELECT v.distinct_id,v.sample,v.session_id,v.control,v.seen_at,v.app_version,v.viewport_class,
        countIf(a.timestamp>=v.seen_at AND dateDiff('second',v.seen_at,a.timestamp)<{SESSION_HOURS*3600})>0 AS acted
      FROM exposures v LEFT JOIN actions a ON v.distinct_id=a.distinct_id AND v.sample=a.sample AND v.session_id=a.session_id AND v.control=a.control
      GROUP BY v.distinct_id,v.sample,v.session_id,v.control,v.seen_at,v.app_version,v.viewport_class)"""
    sql = f""" SELECT p.period,v.sample,v.app_version,v.viewport_class,v.control,count() AS exposed_session_controls,
      uniqExact(v.distinct_id) AS identities,countIf(v.acted)>0 AS any_action,
      countIf(v.acted) AS acted_session_controls,uniqExactIf(v.distinct_id,v.acted) AS acted_identities,
      countIf(dateDiff('second',v.seen_at,{instant(as_of)})>={SESSION_HOURS*3600}) AS mature_exposures
      FROM linked v CROSS JOIN periods p WHERE v.seen_at>=p.period_start AND v.seen_at<p.period_end
      GROUP BY p.period,v.sample,v.app_version,v.viewport_class,v.control ORDER BY exposed_session_controls DESC LIMIT 400"""
    return QueryPlan(common + ctes + sql, {**BASE_FIELDS, 'control': enum(CONTROL_ACTIONS), 'exposed_session_controls': 'count',
        'identities': 'count', 'any_action': 'flag', 'acted_session_controls': 'count', 'acted_identities': 'count', 'mature_exposures': 'count'})


def recovery_plan(common, as_of):
    valid = f"e.timestamp>=i.seen_at AND dateDiff('second',i.seen_at,e.timestamp)<{SESSION_HOURS*3600}"
    resolved = "e.event='ui_obstacle_resolved' AND e.properties.reason=i.reason AND " + valid
    ctes = f""", incidents AS (
      SELECT distinct_id,sample,toString(properties.$session_id) AS session_id,toString(properties.reason) AS reason,
        min(timestamp) AS seen_at,argMin(app_version,timestamp) AS app_version,argMin(viewport_class,timestamp) AS viewport_class,count() AS shows
      FROM e WHERE event='ui_obstacle_seen' AND NOT ({missing('$session_id')}) AND properties.reason IN ({literals(REASONS)})
      GROUP BY distinct_id,sample,session_id,reason), restored AS (
      SELECT i.distinct_id,i.sample,i.session_id,i.reason,i.seen_at,i.app_version,i.viewport_class,i.shows,
        countIf({resolved})>0 AS resolved,minIf(e.timestamp,{resolved}) AS resolved_at,
        countIf({resolved} AND toFloat(e.properties.recovery_ms)>=0) AS recovery_samples,
        sumIf(toFloat(e.properties.recovery_ms),{resolved} AND toFloat(e.properties.recovery_ms)>=0) AS recovery_sum
      FROM incidents i LEFT JOIN e ON i.distinct_id=e.distinct_id AND i.sample=e.sample AND i.session_id=toString(e.properties.$session_id)
      GROUP BY i.distinct_id,i.sample,i.session_id,i.reason,i.seen_at,i.app_version,i.viewport_class,i.shows), continued AS (
      SELECT i.distinct_id,i.sample,i.session_id,i.reason,i.seen_at,i.app_version,i.viewport_class,i.shows,i.resolved,i.recovery_samples,i.recovery_sum,
        countIf(e.event IN ('composer_started','generation_submit_clicked') AND {valid})>0 AS continued,
        countIf(i.resolved AND e.event IN ('composer_started','generation_submit_clicked') AND {valid} AND e.timestamp>=i.resolved_at)>0 AS continued_after_resolution
      FROM restored i LEFT JOIN e ON i.distinct_id=e.distinct_id AND i.sample=e.sample AND i.session_id=toString(e.properties.$session_id)
      GROUP BY i.distinct_id,i.sample,i.session_id,i.reason,i.seen_at,i.app_version,i.viewport_class,i.shows,i.resolved,i.recovery_samples,i.recovery_sum)"""
    sql = f""" SELECT p.period,i.sample,i.app_version,i.viewport_class,i.reason,
      CASE WHEN i.reason IN ({literals(TECHNICAL)}) THEN 'technical' ELSE 'form_or_workflow' END AS obstacle_class,
      count() AS affected_session_categories,uniqExact(i.distinct_id) AS identities,sum(i.shows) AS shows,
      countIf(i.resolved) AS resolved,uniqExactIf(i.distinct_id,i.resolved) AS resolved_identities,
      countIf(i.continued) AS continued,uniqExactIf(i.distinct_id,i.continued) AS continued_identities,
      countIf(i.continued_after_resolution) AS continued_after_resolution,sum(i.recovery_samples) AS recovery_samples,
      sum(i.recovery_sum)/nullIf(sum(i.recovery_samples),0) AS mean_active_recovery_ms,
      countIf(dateDiff('second',i.seen_at,{instant(as_of)})>={SESSION_HOURS*3600}) AS mature_observations
      FROM continued i CROSS JOIN periods p WHERE i.seen_at>=p.period_start AND i.seen_at<p.period_end
      GROUP BY p.period,i.sample,i.app_version,i.viewport_class,i.reason,obstacle_class ORDER BY affected_session_categories DESC LIMIT 400"""
    return QueryPlan(common + ctes + sql, {**BASE_FIELDS, 'reason': enum(REASONS), 'obstacle_class': enum(('technical','form_or_workflow')),
        **{key: 'count' for key in ('affected_session_categories','identities','shows','resolved','resolved_identities','continued',
                                  'continued_identities','continued_after_resolution','recovery_samples','mature_observations')},
        'mean_active_recovery_ms': 'number'})


def results_plan(common, as_of):
    valid = f"e.timestamp>=j.success_at AND dateDiff('second',j.success_at,e.timestamp)<{OBSERVATION_HOURS*3600}"
    ctes = f""", successful_jobs AS (
      SELECT distinct_id,sample,toString(properties.generation_id) AS generation_id,min(timestamp) AS success_at,
        argMin(app_version,timestamp) AS app_version,argMin(viewport_class,timestamp) AS viewport_class,
        argMin({dimension('kind', ('text','image','video','audio'))},timestamp) AS mode,
        argMin({dimension('provider', ('kie','codex','routerai','apimart'))},timestamp) AS provider,
        argMin({model_sql('model_id')},timestamp) AS model_id
      FROM e WHERE event='generation_completed' AND properties.outcome='success' AND NOT ({missing('generation_id')})
      GROUP BY distinct_id,sample,generation_id), result_links AS (
      SELECT j.distinct_id,j.sample,j.generation_id,j.success_at,j.app_version,j.viewport_class,j.mode,j.provider,j.model_id,
        countIf(e.event='result_viewed' AND {valid})>0 AS viewed,
        countIf(e.event='result_action' AND e.properties.action IN ({literals(USE_ACTIONS)}) AND e.properties.outcome='succeeded' AND {valid})>0 AS used,
        countIf(e.event='result_action' AND e.properties.action='download' AND e.properties.outcome='started' AND {valid})>0 AS download_intent
      FROM successful_jobs j LEFT JOIN e ON j.distinct_id=e.distinct_id AND j.sample=e.sample AND j.generation_id=toString(e.properties.generation_id)
      GROUP BY j.distinct_id,j.sample,j.generation_id,j.success_at,j.app_version,j.viewport_class,j.mode,j.provider,j.model_id)"""
    sql = f""" SELECT p.period,j.sample,j.app_version,j.viewport_class,j.mode,j.provider,j.model_id,count() AS successful_jobs,
      uniqExact(j.distinct_id) AS identities,countIf(j.viewed) AS viewed,uniqExactIf(j.distinct_id,j.viewed) AS viewed_identities,
      countIf(j.used) AS used,uniqExactIf(j.distinct_id,j.used) AS used_identities,countIf(j.download_intent) AS download_intent,
      countIf(dateDiff('second',j.success_at,{instant(as_of)})>={OBSERVATION_HOURS*3600}) AS mature_jobs
      FROM result_links j CROSS JOIN periods p WHERE j.success_at>=p.period_start AND j.success_at<p.period_end
      GROUP BY p.period,j.sample,j.app_version,j.viewport_class,j.mode,j.provider,j.model_id ORDER BY successful_jobs DESC LIMIT 400"""
    return QueryPlan(common + ctes + sql, {**BASE_FIELDS, 'mode': enum(('text','image','video','audio')),
        'provider': enum(('kie','codex','routerai','apimart')), 'model_id': 'model',
        **{key:'count' for key in ('successful_jobs','identities','viewed','viewed_identities','used','used_identities','download_intent','mature_jobs')}})


def parameter_plan(common, in_period, join_period):
    rows = []
    dimensions = f"{dimension('provider',('kie','codex','routerai','apimart'))} AS provider,{model_sql('model_id')} AS model_id,{model_sql('selected_model_id')} AS selected_model_id,{dimension('routing_mode',('auto','direct'))} AS routing_mode"
    groups = 'p.period,e.sample,e.app_version,e.viewport_class,provider,model_id,selected_model_id,routing_mode'
    for parameter in PARAMETERS:
        for snapshot, event in (('initial','composer_viewed'),('clicked','generation_submit_clicked'),('effective','generation_submitted')):
            value = f'toString(e.properties.settings.{parameter})'
            origin = dimension(f'parameter_origins.{parameter}', ORIGINS)
            rows.append(f"SELECT p.period,e.sample,e.app_version,e.viewport_class,{dimensions},'{snapshot}' AS snapshot,'{parameter}' AS parameter,'' AS previous_value,{value} AS value,{origin} AS origin,count() AS events,uniqExact(e.distinct_id) AS identities FROM e {join_period} WHERE {in_period} AND e.event='{event}' AND NOT ({missing('settings.'+parameter)}) GROUP BY {groups},value,origin")
    rows.append(f"SELECT p.period,e.sample,e.app_version,e.viewport_class,{dimensions},'change_event' AS snapshot,toString(e.properties.parameter) AS parameter,coalesce(toString(e.properties.previous),'') AS previous_value,toString(e.properties.next) AS value,{dimension('origin',ORIGINS)} AS origin,count() AS events,uniqExact(e.distinct_id) AS identities FROM e {join_period} WHERE {in_period} AND e.event='parameter_changed' AND e.properties.parameter IN ({literals(PARAMETERS)}) GROUP BY {groups},parameter,previous_value,value,origin")
    return QueryPlan(common + ', parameter_rows AS (' + ' UNION ALL '.join(rows) + ') SELECT period,sample,app_version,viewport_class,provider,model_id,selected_model_id,routing_mode,snapshot,parameter,previous_value,value,origin,events,identities FROM parameter_rows ORDER BY events DESC LIMIT 400',
        {**BASE_FIELDS,'provider':enum(('kie','codex','routerai','apimart')),'model_id':'model','selected_model_id':'model','routing_mode':enum(('auto','direct')),
         'snapshot':enum(('initial','clicked','effective','change_event')),'parameter':enum(PARAMETERS),'previous_value':'optional_parameter_value','value':'parameter_value','origin':enum(ORIGINS),'events':'count','identities':'count'})


def comparison_plan(common, in_period, join_period):
    ctes = f""", clicks AS (
      SELECT distinct_id,sample,toString(properties.flow_id) AS flow_id,toString(properties.attempt_id) AS attempt_id,
        min(timestamp) AS clicked_at,argMin(payload,timestamp) AS clicked_payload
      FROM e WHERE event='generation_submit_clicked' AND NOT ({missing('flow_id')}) AND NOT ({missing('attempt_id')})
      GROUP BY distinct_id,sample,flow_id,attempt_id), accepted_snapshots AS (
      SELECT distinct_id,sample,toString(properties.generation_id) AS generation_id,min(e.timestamp) AS timestamp,
        argMin(e.app_version,e.timestamp) AS app_version,argMin(e.viewport_class,e.timestamp) AS viewport_class,argMin(e.payload,e.timestamp) AS accepted_payload
      FROM e WHERE e.event='generation_submitted' AND NOT ({missing('generation_id')}) GROUP BY distinct_id,sample,generation_id), pairs AS (
      SELECT e.distinct_id,e.sample,e.generation_id,e.timestamp,e.app_version,e.viewport_class,e.accepted_payload AS payload,c.clicked_payload,c.clicked_at
      FROM accepted_snapshots e LEFT JOIN clicks c ON e.distinct_id=c.distinct_id AND e.sample=c.sample
        AND toString(e.accepted_payload.flow_id)=c.flow_id AND toString(e.accepted_payload.attempt_id)=c.attempt_id)"""
    rows = []
    for parameter in PARAMETERS:
        effective = f'toString(e.properties.settings.{parameter})'
        clicked = f'toString(e.clicked_properties.settings.{parameter})'
        valid = f"coalesce({clicked},'')!='' AND e.timestamp>=e.clicked_at AND dateDiff('second',e.clicked_at,e.timestamp)<{OBSERVATION_HOURS*3600}"
        rows.append(f"""SELECT p.period,e.sample,e.app_version,e.viewport_class,'{parameter}' AS parameter,
          {dimension('provider',('kie','codex','routerai','apimart'))} AS provider,{model_sql('model_id')} AS model_id,
          count() AS jobs,uniqExact(e.distinct_id) AS identities,countIf({valid}) AS compared_jobs,
          countIf({valid} AND {effective}!={clicked}) AS different_jobs,
          countIf(e.properties.parameter_origins.{parameter} IN ({literals(ORIGINS)})) AS with_origin_jobs,
          countIf(e.properties.parameter_origins.{parameter}='user') AS user_origin_jobs,
          countIf(e.properties.parameter_origins.{parameter}='restored') AS restored_origin_jobs
          FROM pairs e {join_period} WHERE {in_period} AND coalesce({effective},'')!=''
          GROUP BY p.period,e.sample,e.app_version,e.viewport_class,provider,model_id""")
    return QueryPlan(common+ctes+', comparison_rows AS ('+' UNION ALL '.join(rows)+') SELECT period,sample,app_version,viewport_class,parameter,provider,model_id,jobs,identities,compared_jobs,different_jobs,with_origin_jobs,user_origin_jobs,restored_origin_jobs FROM comparison_rows ORDER BY jobs DESC LIMIT 400',
        {**BASE_FIELDS,'parameter':enum(PARAMETERS),'provider':enum(('kie','codex','routerai','apimart')),'model_id':'model',
         **{key:'count' for key in ('jobs','identities','compared_jobs','different_jobs','with_origin_jobs','user_origin_jobs','restored_origin_jobs')}})


def coverage_plan(start, report_end, as_of):
    flow_events = ('composer_viewed','composer_started','composer_left','generation_submit_clicked','generation_submit_prevented','generation_submitted')
    attempt_events = ('generation_submit_clicked','generation_submit_prevented','generation_submitted')
    generation_events = (*FAMILIES['server'],*FAMILIES['results'])
    ui_events = tuple(event for event in EVENTS if event not in FAMILIES['server'])
    diagnostic = {'missing_flow': f"event IN ({literals(flow_events)}) AND ({missing('flow_id')})",
                  'missing_attempt': f"event IN ({literals(attempt_events)}) AND ({missing('attempt_id')})",
                  'missing_generation': f"event IN ({literals(generation_events)}) AND ({missing('generation_id')})",
                  'missing_session': f"event IN ({literals(ui_events)}) AND ({missing('$session_id')})",
                  'missing_origin_session': f"event IN ({literals(FAMILIES['server'])}) AND ({missing('origin_session_id')})",
                  'non_account_identity': "NOT startsWith(distinct_id,'u_')"}
    for key in ('app_version','viewport_class','ui_mode','release_channel','selected_model_id','provider','model_id','settings','parameter_origins','origin','recovery_ms','load_time_ms','result_count',
                'section','from_section','to_section','entry_point','menu','control','click_region','element_type','mode','kind','routing_mode','category',
                'selection_made','search_used','parameter','previous','next','draft_source','action','entity','outcome','scope','source_type','source_count',
                'source_mode','reason','stage','input_method','help','setting','value','duration_ms','active_ms','quote_credits','quote_status','locale'):
        diagnostic['with_'+key] = f'NOT ({missing(key)})'
    for key,values in {'viewport_class':('mobile','medium','wide'),'ui_mode':('user','admin','admin_preview'),
                       'release_channel':('release','debug'),'provider':('kie','codex','routerai','apimart'),
                       'routing_mode':('auto','direct'),'mode':('text','image','video','audio'), 'origin':ORIGINS}.items():
        diagnostic['unsupported_'+key] = f"NOT ({missing(key)}) AND toString(properties.{key}) NOT IN ({literals(values)})"
    diagnostic['unsupported_app_version'] = f"NOT ({missing('app_version')}) AND NOT match(toString(properties.app_version),'^[0-9][A-Za-z0-9.+_-]{{0,39}}$')"
    diagnostic['inconsistent_debug_collection'] = "properties.collection_mode='debug_assumed' AND properties.release_channel!='debug'"
    unknown = f"length(arrayFilter(k -> NOT k IN ({literals(KNOWN_PROPERTIES)}),JSONExtractKeys(payload)))"
    diagnostic['events_with_unrecognized_properties'] = unknown+' > 0'
    columns = ','.join(f'uniqExactIf(uuid,{condition}) AS {name}' for name,condition in diagnostic.items())
    sql = f"""SELECT {sample_sql()} AS sample,{family_sql()} AS family,event,
      CASE WHEN toString(properties.schema_version)='2' THEN 'v2' WHEN toString(properties.schema_version)='1' THEN 'v1' ELSE 'unsupported' END AS schema,
      count() AS deliveries,uniqExact(uuid) AS events,uniqExact(distinct_id) AS identities,
      max(timestamp) AS last_event,{columns},
      uniqExactIf(uuid,properties.collection_mode='debug_assumed') AS debug_assumed_events,
      uniqExactIf(uuid,{missing('collection_mode')}) AS collection_mode_unspecified,
      uniqExactIf(uuid,toString(properties.collection_mode) NOT IN ('','debug_assumed') AND NOT ({missing('collection_mode')})) AS collection_mode_other
      FROM (SELECT uuid,event,timestamp,distinct_id,properties AS payload FROM events) raw_events
      WHERE timestamp>={instant(start)} AND timestamp<{instant(as_of)} AND event IN ({literals(EVENTS)})
      GROUP BY sample,family,event,schema ORDER BY events DESC LIMIT 400"""
    return QueryPlan(sql, {'sample':BASE_FIELDS['sample'],'family':enum(FAMILIES),'event':enum(EVENTS),
        'schema':enum(('v1','v2','unsupported')),'deliveries':'count','events':'count','identities':'count','last_event':'timestamp',
        **{key:'count' for key in diagnostic},'debug_assumed_events':'count','collection_mode_unspecified':'count','collection_mode_other':'count'})
