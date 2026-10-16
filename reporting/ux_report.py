"""Public aggregate assembly, coverage and explicit denominators."""
import asyncio
import json
from datetime import datetime, timezone
from time import monotonic

from reporting.aggregate_safety import validate_rows
from reporting.ux_contract import EVENTS, FAMILIES, OBSERVATION_HOURS, SAMPLES, SESSION_HOURS, UNAVAILABLE, USE_ACTIONS
from reporting.ux_queries import plans
from reporting.queries import report_metadata

BLOCK_QUERIES = {
    'journey': ('journey','preparation_events','server_events'),
    'navigation': ('navigation_events','discovery'),
    'model_parameters': ('configuration_events','parameters','parameter_comparison','server_events'),
    'obstacles_recovery': ('obstacle_events','recovery'),
    'history_results': ('organization_events','result_events','successful_results','account_queue_events'),
}


def ratio(numerator, denominator, unit):
    return {'numerator': numerator, 'denominator': denominator, 'denominator_unit': unit,
            'percent': round(100*numerator/denominator, 2) if denominator else None}


def add_rates(name, row, totals):
    row = dict(row)
    rates = {}
    if name == 'journey':
        row['immature_preparations'] = row['preparations'] - row['mature_preparations']
        # Missing UI is an observation gap, never automatically a failure.
        for stage in ('attempted','accepted','successful','viewed','used','download_intent'):
            rates[stage+'_observed'] = ratio(row[stage],row['preparations'],'preparations')
            rates[stage+'_mature'] = ratio(row['mature_'+stage],row['mature_preparations'],'mature_preparations')
            rates[stage+'_identities'] = ratio(row[stage+'_identities'],row['identities'],'account_identities')
    elif name == 'discovery':
        rates['acted'] = ratio(row['acted_session_controls'],row['exposed_session_controls'],'identity_session_control_observations')
        rates['acted_identities'] = ratio(row['acted_identities'],row['identities'],'exposed_account_identities')
        row['immature_exposures'] = row['exposed_session_controls']-row['mature_exposures']
    elif name == 'recovery':
        for stage in ('resolved','continued','continued_after_resolution'):
            rates[stage] = ratio(row[stage],row['affected_session_categories'],'identity_session_reason_observations')
        rates['resolved_identities'] = ratio(row['resolved_identities'],row['identities'],'affected_account_identities')
        rates['continued_identities'] = ratio(row['continued_identities'],row['identities'],'affected_account_identities')
        row['immature_observations'] = row['affected_session_categories']-row['mature_observations']
    elif name == 'successful_results':
        for stage in ('viewed','used','download_intent'):
            rates[stage] = ratio(row[stage],row['successful_jobs'],'successful_jobs')
        for stage in ('viewed','used'):
            rates[stage+'_identities'] = ratio(row[stage+'_identities'],row['identities'],'successful_result_account_identities')
        row['immature_jobs'] = row['successful_jobs']-row['mature_jobs']
    elif name == 'parameter_comparison':
        row['uncompared_jobs'] = row['jobs']-row['compared_jobs']
        row['missing_origin_jobs'] = row['jobs']-row['with_origin_jobs']
        rates['effective_differs'] = ratio(row['different_jobs'],row['compared_jobs'],'jobs_with_both_parameter_values')
        rates['manual_origin'] = ratio(row['user_origin_jobs'],row['with_origin_jobs'],'accepted_jobs_with_parameter_origin')
    elif name.endswith('_events'):
        family = next(family for family, events in FAMILIES.items() if row['event'] in events)
        denominator = totals.get((row['period'],row['sample'],family))
        rates['family_events'] = ratio(row['events'],denominator['events'] if denominator else None,'family_events')
        rates['family_identities'] = ratio(row['identities'],denominator['identities'] if denominator else None,'family_account_identities')
        rates['empty_search'] = ratio(row['empty_search'],row['search_samples'],'search_events_with_result_count')
        rates['closed_without_selection'] = ratio(row['no_selection'],row['selection_samples'],'picker_closed_events_with_selection_flag')
        if row['event'] == 'model_selected':
            row['manual_selection_events'] = None if row['origin']=='unknown' else row['events'] if row['origin']=='user' else 0
    elif name == 'parameters':
        row['manual_change_events'] = None if row['snapshot']=='change_event' and row['origin']=='unknown' else row['events'] if row['snapshot']=='change_event' and row['origin']=='user' else 0
        denominator = totals.get((row['period'],row['sample'],'all'))
        rates['identities'] = ratio(row['identities'],denominator['identities'] if denominator else None,'sample_account_identities')
    row['rates'] = rates
    return row


async def collect(client, end_day, as_of, zone, deadline=None, max_bytes=512_000):
    query_plans = plans(end_day, as_of, zone)
    periods = report_metadata(end_day,zone)['periods']
    data, query_status, errors = {}, {}, {}
    for name, plan in query_plans.items():
        try:
            if deadline is not None:
                remaining = deadline-monotonic()
                if remaining <= 1:
                    raise RuntimeError('Query budget exhausted')
                client.timeout = min(45,remaining)
            rows = await asyncio.to_thread(client.query,plan.sql)
            data[name] = validate_rows(rows,plan.fields,plan.limit)
            truncated = bool(getattr(rows,'truncated',False) or len(rows)>=plan.limit)
            query_status[name] = {'status': 'available' if rows else 'available_empty',
                                  'truncated': truncated, 'limit': plan.limit, 'returned_rows': len(rows)}
        except (RuntimeError,ValueError):
            errors[name] = 'Aggregate query unavailable or invalid'
            query_status[name] = {'status':'unavailable','truncated':None,'limit':plan.limit,'returned_rows':None}
    totals = {(row['period'],row['sample'],row['family']):row for row in data.get('totals',[])}
    totals_usable = 'totals' in data and not query_status['totals']['truncated']
    if totals_usable:
        for period in ('report_day','previous_day','baseline'):
            for sample in SAMPLES:
                for family in (*FAMILIES,'all'):
                    totals.setdefault((period,sample,family), {'period':period,'sample':sample,'family':family,
                        'events':0,'identities':0,'deliveries':0})
    else:
        totals = {}
    coverage_rows = data.get('coverage',[])
    diagnostics = {'query_status':query_status,'errors':errors,'event_coverage':[],
                   'freshness_period':{'start':periods['legacy_window']['start'],'end_exclusive':as_of.astimezone(timezone.utc).isoformat()},
                   'unavailable_measurements':UNAVAILABLE}
    coverage_usable = 'coverage' in data and not query_status['coverage']['truncated']
    index = {(r['sample'],r['event'],r['schema']):r for r in coverage_rows}
    for sample in SAMPLES:
        for event in EVENTS:
            row = index.get((sample,event,'v2'))
            diagnostics['event_coverage'].append({'sample':sample,'event':event,
                'family':next(f for f,events in FAMILIES.items() if event in events),
                'status':'observed' if row else 'zero_observed' if coverage_usable else 'unknown',
                'last_event':row['last_event'] if row else None,
                'events':row['events'] if row else 0 if coverage_usable else None})
    diagnostics['coverage_rows'] = coverage_rows
    diagnostics['family_coverage'] = []
    for sample in SAMPLES:
        for family in FAMILIES:
            observed = [r for r in coverage_rows if r['sample']==sample and r['family']==family and r['schema']=='v2']
            latest = max((r['last_event'] for r in observed),default=None)
            age = None
            if latest:
                stamp = datetime.fromisoformat(latest.replace('Z','+00:00'))
                if stamp.tzinfo is None:
                    stamp = stamp.replace(tzinfo=timezone.utc)
                age = max(0,(as_of-stamp).total_seconds())
            diagnostics['family_coverage'].append({'sample':sample,'family':family,
                'status':'observed' if observed else 'zero_observed' if coverage_usable else 'unknown',
                'last_event':latest,'age_seconds':age})
    blocks = {}
    for block, names in BLOCK_QUERIES.items():
        failed = [name for name in (*names,'totals','coverage') if name not in data]
        truncated = [name for name in (*names,'totals','coverage') if query_status[name]['truncated']]
        rows = {name:[add_rates(name,row,totals) for row in data.get(name,[])] for name in names if name in data}
        missing_families = []
        # Zero is distinct from a query failure but cannot prove capture is configured.
        for family in FAMILIES:
            if any(event in FAMILIES[family] for name in names for event in required_events(name)):
                if not any(row['schema']=='v2' and row['family']==family for row in coverage_rows):
                    missing_families.append(family)
        blocks[block] = {'status':'unavailable' if all(name not in data for name in names) else 'partial' if failed or truncated else 'available',
                         'rows':rows,'failed_queries':failed,'truncated_queries':truncated,
                         'families_without_observed_v2_events':missing_families,
                         'sample_status':{sample:('observed' if any(row['sample']==sample for values in rows.values() for row in values)
                                                  else 'zero_observed' if not failed and not truncated else 'unknown') for sample in SAMPLES}}
        dependency_events = set(event for name in names for event in required_events(name))
        keys = {'journey':('missing_flow','missing_attempt','missing_generation'),
                'navigation':('missing_session',),'model_parameters':('missing_flow','missing_attempt','missing_generation'),
                'obstacles_recovery':('missing_session',),'history_results':('missing_generation',)}[block]
        missing_links = {key:sum(row[key] for row in coverage_rows if row['schema']=='v2' and row['event'] in dependency_events)
                         for key in keys}
        blocks[block]['linkage'] = {'status':'partial' if any(missing_links.values()) else 'available' if coverage_usable else 'unknown',
                                   'missing_events_by_property':missing_links if coverage_usable else None}
        if any(missing_links.values()) and blocks[block]['status']=='available':
            blocks[block]['status']='partial'
    has_link_gaps = any(block['linkage']['status']=='partial' for block in blocks.values())
    report = {'contract_version':2,'schema_version':2,'as_of':as_of.astimezone(timezone.utc).isoformat(),
            'observation':{'journey_hours':OBSERVATION_HOURS,'result_hours':OBSERVATION_HOURS,'session_hours':SESSION_HOURS,
                           'immature_is_failure':False,'use_actions':list(USE_ACTIONS),
                           'use_outcome':'succeeded','download_started':'intent_only'},
            'samples':list(SAMPLES),'totals':list(totals.values()) if totals_usable else None,
            'periods':{key:value for key,value in periods.items() if key!='legacy_window'},
            'control_action_mapping':{'model_picker':{'event':'model_picker_opened'},
                'parameters':{'event':'parameter_changed','origin':'user'},'sources':{'event':'source_action'},
                'queue':{'event':'queue_action'},'result_actions':{'event':'result_action'},'generate':{'event':'generation_submit_clicked'}},
            'coverage':{'status':'unavailable' if not data else 'partial' if errors or has_link_gaps or any(status['truncated'] for status in query_status.values())
                        else 'available' if any(row['schema']=='v2' for row in coverage_rows) else 'zero_observed',
                        'query_complete':not errors and not any(status['truncated'] for status in query_status.values()),
                        'complete':not errors and not has_link_gaps and not any(status['truncated'] for status in query_status.values()),
                        'observed_v2':any(row['schema']=='v2' and row['events']>0 for row in coverage_rows) if coverage_usable else None,
                        'measurement_is_exhaustive':False},
            'blocks':blocks,'diagnostics':diagnostics}
    return bound_output(report,max_bytes)


def bound_output(report,max_bytes):
    """Bound compact public JSON as well as SQL group cardinality."""
    report['limits'] = {'per_query_rows':400,'compact_json_bytes':max_bytes,'output_truncated':False}
    def size(value):
        return len(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode('utf-8'))
    while size(report)>max_bytes:
        candidates = {}
        for block in report['blocks'].values():
            for name,rows in block['rows'].items():
                if rows:
                    candidates.setdefault(name,[]).append(rows)
        if report['diagnostics']['coverage_rows']:
            candidates['coverage'] = [report['diagnostics']['coverage_rows']]
        if not candidates:
            # Fixed inventories/periods themselves fit the production limit.
            raise ValueError('Configured output budget cannot contain coverage inventory')
        name = max(candidates,key=lambda key:sum(size(rows) for rows in candidates[key]))
        included = len(candidates[name][0])//2
        for rows in candidates[name]:
            del rows[included:]
        status = report['diagnostics']['query_status'][name]
        status['output_truncated'] = True
        status['included_rows'] = included
        status['truncated'] = True
        for block in report['blocks'].values():
            if name in block['rows'] or name=='coverage':
                if name not in block['truncated_queries']:
                    block['truncated_queries'].append(name)
                if block['status']!='unavailable':
                    block['status']='partial'
        report['coverage'].update(status='partial',complete=False)
        report['limits']['output_truncated'] = True
    return report


def required_events(name):
    # Diagnostic dependency inventory, separate from query availability.
    dependencies = {
        'journey': ('composer_started','generation_submit_clicked','generation_submitted','generation_completed','result_viewed','result_action'),
        'discovery': ('control_viewed','model_picker_opened','parameter_changed','source_action','queue_action','result_action','generation_submit_clicked'),
        'recovery': ('ui_obstacle_seen','ui_obstacle_resolved','composer_started','generation_submit_clicked'),
        'successful_results': ('generation_completed','result_viewed','result_action'),
        'parameters': ('composer_viewed','generation_submit_clicked','generation_submitted','parameter_changed'),
        'parameter_comparison': ('generation_submit_clicked','generation_submitted'),
    }
    if name in dependencies:
        return dependencies[name]
    stem = name.removesuffix('_events')
    return FAMILIES.get({'configuration':'configuration','obstacle':'obstacles','result':'results',
                         'preparation':'preparation','server':'server','account_queue':'account_queue',
                         'navigation':'navigation','organization':'organization'}.get(stem,''),())
