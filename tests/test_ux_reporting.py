import asyncio
import json
import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch

from reporting.aggregate_safety import validate_rows
from reporting.posthog import QueryRows
from reporting.ux_queries import plans
from reporting.ux_report import collect
from ux_sqlite import SyntheticPostHog

END=date(2026,10,10)
AS_OF=datetime(2026,10,12,9,tzinfo=timezone.utc)


def event(name,at='2026-10-09 06:00:00',identity='u_account',uuid=None,**properties):
    return {'uuid':uuid or name+at+str(properties),'event':name,'timestamp':at,'distinct_id':identity,
            'properties':{'schema_version':2,'ui_mode':'user','release_channel':'release','app_version':'1.2.3',
                          'viewport_class':'wide','$session_id':'session','flow_id':'flow','attempt_id':'attempt',**properties}}


def full_path(**sample):
    return [event('composer_started',**sample),event('generation_submit_clicked',at='2026-10-09 06:01:00',**sample),
        event('generation_submitted',at='2026-10-09 06:02:00',generation_id='g_job',provider='codex',kind='text',**sample),
        event('generation_completed',at='2026-10-10 06:00:00',generation_id='g_job',outcome='success',provider='codex',kind='text',**sample),
        event('result_viewed',at='2026-10-10 06:01:00',generation_id='g_job',**sample),
        event('result_action',at='2026-10-10 06:02:00',generation_id='g_job',action='copy_result',outcome='succeeded',**sample)]


class SQLTests(unittest.TestCase):
    def query(self,name,events,as_of=AS_OF):
        plan=plans(END,as_of)[name]
        rows=SyntheticPostHog(events).query(plan.sql)
        return validate_rows(rows,plan.fields,plan.limit)

    def test_all_production_queries_execute_on_empty_dataset(self):
        client=SyntheticPostHog()
        for name,plan in plans(END,AS_OF).items():
            with self.subTest(query=name):
                self.assertEqual(validate_rows(client.query(plan.sql),plan.fields,plan.limit),[])
                self.assertNotIn('SELECT *',plan.sql)
                self.assertNotIn('person.properties',plan.sql)

    def test_connected_full_path_and_next_day_completion(self):
        row=self.query('journey',full_path())[0]
        self.assertEqual(row['preparations'],1)
        self.assertEqual(row['attempt_count'],1)
        for stage in ('attempted','accepted','successful','viewed','used'):
            self.assertEqual(row[stage],1)
            self.assertEqual(row['mature_'+stage],1)
        # Completion belongs to the following day, but stays in the preparation cohort.
        self.assertEqual(row['period'],'report_day')

    def test_model_catalog_slices_preserve_safe_ids_and_hide_unsafe_values(self):
        safe=('gpt-6-sol','~gpt-6-sol','provider/model.v2:fast')
        unsafe=('https://private.example/source','a..b','private prompt or title','a'*101)
        for model in (*safe,*unsafe):
            with self.subTest(model_kind='safe' if model in safe else 'unsafe'):
                events=[event('model_selected',model_id=model,selected_model_id=model),
                        event('generation_submitted',model_id=model,selected_model_id=model,
                              provider='codex',kind='text',generation_id='g_job')]
                expected=model if model in safe else 'unknown'
                for query in ('configuration_events','server_events'):
                    rows=self.query(query,events)
                    self.assertTrue(rows)
                    self.assertTrue(all(row['model_id']==expected and row['selected_model_id']==expected
                                        for row in rows))

    def test_multiple_attempts_one_flow_do_not_multiply_preparations(self):
        events=full_path()+[event('generation_submit_clicked',at='2026-10-09 06:00:30',attempt_id='attempt-2'),
                           event('generation_submit_prevented',at='2026-10-09 06:00:31',attempt_id='attempt-2',reason='balance')]
        row=self.query('journey',events)[0]
        self.assertEqual(row['preparations'],1)
        self.assertEqual(row['attempt_count'],2)
        self.assertEqual(row['used'],1)

    def test_population_identity_flow_attempt_and_job_are_all_required(self):
        for field,value,index in [('ui_mode','admin',2),('release_channel','debug',2),('flow_id','other',2),
                                  ('attempt_id','other',2),('generation_id','other',3)]:
            events=full_path()
            events[index]['properties'][field]=value
            row=self.query('journey',events)[0]
            self.assertEqual(row['used'],0,(field,value))
        events=full_path();events[2]['distinct_id']='u_other'
        self.assertEqual(self.query('journey',events)[0]['accepted'],0)

    def test_debug_is_not_synthetic_and_admin_is_separate(self):
        events=[]
        for index,(mode,channel) in enumerate([('user','release'),('user','debug'),('admin','debug'),('admin_preview','release')]):
            path=full_path(ui_mode=mode,release_channel=channel)
            for e in path: e['uuid']+=str(index)
            events+=path
        rows=self.query('journey',events)
        self.assertEqual({r['sample'] for r in rows},{'user_release','user_debug','admin_debug','admin_preview_release'})
        self.assertTrue(all(r['used']==1 for r in rows))

    def test_repeated_uuid_deduplicates_before_linkage_and_counts_delivery(self):
        events=full_path();events.append(events[0])
        self.assertEqual(self.query('journey',events)[0]['preparations'],1)
        row=next(r for r in self.query('preparation_events',events) if r['event']=='composer_started')
        self.assertEqual((row['events'],row['deliveries']),(1,2))

    def test_missing_ui_and_link_properties_are_not_invented(self):
        events=full_path();events.pop(1)
        row=self.query('journey',events)[0]
        self.assertEqual((row['attempted'],row['accepted'],row['successful']),(0,0,0))
        events=full_path();del events[2]['properties']['generation_id']
        coverage=self.query('coverage',events)
        row=next(r for r in coverage if r['event']=='generation_submitted')
        self.assertEqual(row['missing_generation'],1)
        self.assertEqual(self.query('journey',events)[0]['accepted'],0)

    def test_immature_and_outside_window_are_not_failures(self):
        row=self.query('journey',full_path(),datetime(2026,10,10,9,tzinfo=timezone.utc))[0]
        self.assertEqual(row['mature_preparations'],0)
        events=full_path();events[-1]['timestamp']='2026-10-11 07:00:00'
        self.assertEqual(self.query('journey',events)[0]['used'],0)

    def test_stages_cannot_be_borrowed_from_different_jobs(self):
        events=full_path()
        events[-1]['properties']['generation_id']='g_other'
        events.append(event('generation_submitted',at='2026-10-09 06:03:00',generation_id='g_other'))
        self.assertEqual(self.query('journey',events)[0]['used'],0)

    def test_navigation_explicit_mapping_same_session_and_after_visibility(self):
        events=[event('control_viewed',control='model_picker'),event('model_picker_opened',at='2026-10-09 06:01:00')]
        self.assertEqual(self.query('discovery',events)[0]['acted_session_controls'],1)
        events[-1]['properties']['$session_id']='other-session'
        self.assertEqual(self.query('discovery',events)[0]['acted_session_controls'],0)
        events[-1]=event('ui_clicked',at='2026-10-09 06:01:00',click_region='model_picker',element_type='button')
        self.assertEqual(self.query('discovery',events)[0]['acted_session_controls'],0)

    def test_recovery_temporal_category_and_technical_separation(self):
        events=[event('ui_obstacle_resolved',at='2026-10-09 05:00:00',reason='upload',recovery_ms=9),
                event('ui_obstacle_seen',reason='upload'),
                event('ui_obstacle_resolved',at='2026-10-09 06:01:00',reason='upload',recovery_ms=500),
                event('generation_submit_clicked',at='2026-10-09 06:02:00')]
        row=self.query('recovery',events)[0]
        self.assertEqual(row['obstacle_class'],'technical')
        self.assertEqual(row['mean_active_recovery_ms'],500)
        self.assertEqual(row['continued_after_resolution'],1)
        events[2]['properties']['reason']='balance'
        self.assertEqual(self.query('recovery',events)[0]['resolved'],0)

    def test_restored_and_normalized_settings_do_not_become_manual(self):
        events=[event('composer_viewed',settings={'count':2},parameter_origins={'count':'restored'}),
                event('generation_submit_clicked',at='2026-10-09 06:01:00',settings={'count':2},parameter_origins={'count':'restored'}),
                event('generation_submitted',at='2026-10-09 06:02:00',generation_id='g_job',settings={'count':1},parameter_origins={'count':'restored'})]
        rows=self.query('parameters',events)
        self.assertEqual({r['snapshot'] for r in rows},{'initial','clicked','effective'})
        self.assertTrue(all(r['origin']=='restored' for r in rows))
        row=self.query('parameter_comparison',events)[0]
        self.assertEqual((row['different_jobs'],row['user_origin_jobs'],row['restored_origin_jobs']),(1,0,1))

    def test_download_started_only_means_intent(self):
        events=full_path();events[-1]['properties'].update(action='download',outcome='started')
        row=self.query('journey',events)[0]
        self.assertEqual((row['used'],row['download_intent']),(0,1))

    def test_selection_search_readiness_and_manual_changes(self):
        events=[event('model_selected',model_id='codex:model',selected_model_id='codex:model',routing_mode='direct',origin='restored'),
                event('model_picker_closed',selection_made=False,duration_ms=5000),
                event('model_search_used',result_count=0),event('screen_ready',section='home',load_time_ms=120),
                event('parameter_changed',parameter='count',previous=1,next=2,origin='user')]
        rows=self.query('configuration_events',events)
        closed=next(r for r in rows if r['event']=='model_picker_closed')
        self.assertEqual((closed['no_selection'],closed['selection_samples'],closed['mean_duration_ms']),(1,1,5000))
        search=next(r for r in rows if r['event']=='model_search_used')
        self.assertEqual((search['empty_search'],search['search_samples']),(1,1))
        row=self.query('parameters',events)[0]
        self.assertEqual((row['previous_value'],row['value'],row['origin']),('1','2','user'))
        self.assertEqual(self.query('navigation_events',events)[0]['mean_load_ms'],120)

    def test_schema_versions_and_missing_dimensions_remain_explicit(self):
        events=[event('generation_submitted',schema_version=1,generation_id='g_old'),
                event('generation_submitted',generation_id='g_new',viewport_class='invalid')]
        rows=self.query('server_events',events)
        self.assertEqual(sum(r['events'] for r in rows),1)
        self.assertEqual(rows[0]['viewport_class'],'unknown')
        coverage=self.query('coverage',events)
        self.assertEqual({r['schema'] for r in coverage},{'v1','v2'})
        self.assertEqual(next(r for r in coverage if r['schema']=='v2')['unsupported_viewport_class'],1)


class AssemblyTests(unittest.IsolatedAsyncioTestCase):
    async def test_serialized_output_budget_is_explicit(self):
        events=[]
        for index in range(80):
            path=full_path(app_version=f'1.2.{index}')
            for e in path:
                e['distinct_id']=f'u_account_{index}'
                e['uuid']+=str(index)
            events+=path
        result=await collect(SyntheticPostHog(events),END,AS_OF,'Europe/Moscow',max_bytes=128_000)
        self.assertLessEqual(len(json.dumps(result,separators=(',',':')).encode()),128_000)
        self.assertTrue(result['limits']['output_truncated'])
        self.assertFalse(result['coverage']['complete'])
        self.assertTrue(any(s.get('output_truncated') for s in result['diagnostics']['query_status'].values()))

    async def test_zero_partial_failure_truncation_and_no_raw_payload(self):
        result=await collect(SyntheticPostHog(),END,AS_OF,'Europe/Moscow')
        self.assertTrue(result['coverage']['complete'])
        self.assertEqual(result['coverage']['status'],'zero_observed')
        self.assertTrue(all(row['identities']==0 for row in result['totals']))
        class PartialClient(SyntheticPostHog):
            def query(self,sql):
                if 'per_flow AS' in sql: raise RuntimeError('PRIVATE SQL/token')
                return super().query(sql)
        result=await collect(PartialClient(full_path()),END,AS_OF,'Europe/Moscow')
        self.assertFalse(result['coverage']['complete'])
        self.assertEqual(result['blocks']['journey']['status'],'partial')
        self.assertNotIn('PRIVATE',json.dumps(result))
        class TruncatedClient(SyntheticPostHog):
            def query(self,sql): return QueryRows(super().query(sql),truncated=True)
        result=await collect(TruncatedClient(full_path()),END,AS_OF,'Europe/Moscow')
        self.assertFalse(result['coverage']['complete'])
        self.assertTrue(result['diagnostics']['query_status']['journey']['truncated'])
        self.assertIsNone(result['totals'])
        events=full_path()
        for e in events: e['properties'].update(prompt='PRIVATE prompt',query='PRIVATE search',url='https://private.example')
        result=await collect(SyntheticPostHog(events),END,AS_OF,'Europe/Moscow')
        encoded=json.dumps(result)
        for value in ('PRIVATE','u_account','g_job','https://private.example'):
            self.assertNotIn(value,encoded)
        self.assertTrue(all(r['events_with_unrecognized_properties']>0 for r in result['diagnostics']['coverage_rows']))
        for row in result['blocks']['journey']['rows']['journey']:
            self.assertEqual(row['rates']['used_observed']['denominator'],1)

    async def test_missing_or_unsafe_query_output_is_unavailable_not_zero(self):
        class UnsafeClient(SyntheticPostHog):
            def query(self,sql):
                rows=super().query(sql)
                return [{**row,'distinct_id':'private-identity'} for row in rows]
        result=await collect(UnsafeClient(full_path()),END,AS_OF,'Europe/Moscow')
        self.assertFalse(result['coverage']['complete'])
        self.assertNotIn('private-identity',json.dumps(result))

    async def test_link_gaps_have_separate_coverage_status(self):
        events=full_path();del events[2]['properties']['attempt_id']
        result=await collect(SyntheticPostHog(events),END,AS_OF,'Europe/Moscow')
        self.assertTrue(result['coverage']['query_complete'])
        self.assertFalse(result['coverage']['complete'])
        self.assertEqual(result['blocks']['journey']['linkage']['missing_events_by_property']['missing_attempt'],1)
        self.assertEqual(result['blocks']['journey']['status'],'partial')
