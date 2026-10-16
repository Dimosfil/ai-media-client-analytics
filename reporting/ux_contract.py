"""Reporting projection of the verified AI Media Client schema-v2 contract.

Source provenance and deliberately unavailable measurements: docs/report-contract.md.
This module does not define new application events or accept caller-selected fields.
"""
from dataclasses import dataclass

FAMILIES = {
    'navigation': ('navigation_clicked', 'screen_viewed', 'screen_ready', 'menu_opened', 'control_viewed', 'ui_clicked'),
    'configuration': ('model_picker_opened', 'model_search_used', 'model_selected', 'model_picker_closed', 'mode_selected', 'parameter_changed'),
    'preparation': ('composer_viewed', 'composer_started', 'composer_left', 'source_action', 'quote_shown', 'generation_submit_clicked', 'generation_submit_prevented'),
    'obstacles': ('ui_obstacle_seen', 'ui_obstacle_resolved', 'help_opened'),
    'organization': ('workspace_action', 'search_used', 'history_action'),
    'results': ('result_viewed', 'result_action'),
    'account_queue': ('profile_action', 'settings_changed', 'settings_saved', 'queue_action'),
    'server': ('generation_submitted', 'generation_completed', 'generation_blocked', 'generation_outcome_unknown'),
}
EVENTS = tuple(event for events in FAMILIES.values() for event in events)
SAMPLES = ('user_release', 'user_debug', 'admin_release', 'admin_debug',
           'admin_preview_release', 'admin_preview_debug', 'unknown_population')
SECTIONS = ('landing', 'home', 'movie', 'workspace', 'history', 'spending', 'profile', 'plans', 'archive', 'settings', 'telegram')
CONTROLS = ('model_picker', 'parameters', 'advanced_settings', 'sources', 'queue', 'result_actions', 'generate')
ACTIONS = ('create', 'open', 'rename', 'move', 'archive', 'restore', 'delete', 'load_more', 'download',
           'copy_prompt', 'copy_result', 'favorite', 'unfavorite', 'reuse', 'expand', 'play', 'pause',
           'resume', 'view', 'remove', 'clear', 'select', 'change_mode', 'add', 'transfer', 'save',
           'telegram_link', 'telegram_unlink', 'sign_out')
REASONS = ('models_unavailable', 'model_missing', 'required_fields', 'invalid_parameters', 'source_conflict',
           'source_validation', 'upload', 'quote_unavailable', 'quote_pending', 'auto_unavailable', 'balance',
           'service_unavailable', 'selection_changed', 'transport_unknown', 'busy', 'navigation', 'chat_changed', 'pagehide')
TECHNICAL = ('models_unavailable', 'upload', 'quote_unavailable', 'service_unavailable', 'transport_unknown')
ORIGINS = ('default', 'restored', 'reuse', 'template', 'user')
PARAMETERS = ('model_id', 'aspect_ratio', 'reasoning', 'speed', 'resolution', 'duration', 'count', 'output_format')
USE_ACTIONS = ('copy_result', 'reuse', 'favorite', 'play')
CONTROL_ACTIONS = {
    'model_picker': "event = 'model_picker_opened'",
    'parameters': "event = 'parameter_changed' AND properties.origin = 'user'",
    'sources': "event = 'source_action'",
    'queue': "event = 'queue_action'",
    'result_actions': "event = 'result_action'",
    'generate': "event = 'generation_submit_clicked'",
}
OBSERVATION_HOURS = 48
SESSION_HOURS = 24
ROW_LIMIT = 400
KNOWN_PROPERTIES = ('schema_version','app_version','release_channel','collection_mode','ui_mode','locale','viewport_class',
    '$session_id','origin_session_id','flow_id','attempt_id','generation_id','section','from_section','to_section','entry_point',
    'menu','control','click_region','element_type','mode','kind','provider','channel','routing_mode','model_id','selected_model_id',
    'category','selection_made','search_used','result_count','parameter','previous','next','origin','draft_source','settings',
    'parameter_origins','action','entity','outcome','scope','source_type','source_count','source_mode','reason','stage','input_method',
    'help','setting','value','duration_ms','active_ms','load_time_ms','recovery_ms','quote_credits','quote_status',
    '$lib','$lib_version','$geoip_disable','$process_person_profile','$ip')


def enum(values):
    return 'enum:' + '|'.join((*values, 'unknown'))


BASE_FIELDS = {'period': enum(('report_day', 'previous_day', 'baseline')),
               'sample': enum(SAMPLES), 'app_version': 'version',
               'viewport_class': enum(('mobile', 'medium', 'wide'))}


@dataclass(frozen=True)
class QueryPlan:
    sql: str
    fields: dict
    limit: int = ROW_LIMIT


UNAVAILABLE = [
    'No confirmed synthetic-scenario property in the canonical contract; debug is not classified as synthetic.',
    'No explicit service-available property; no_observed_technical_obstacle does not establish service availability.',
    'No automatic-normalization event or cause: clicked versus effective settings are compared, not attributed.',
    'No dedicated advanced_settings action to pair with control_viewed.',
    'No obstacle occurrence ID: recovery is measured per identity/session/reason, not individual recurring episodes.',
    'No search relevance/found-target property; nonempty results are not search success.',
    'No browser-confirmed file-save property; download started is intent.',
    'Properties discarded before capture cannot be counted from PostHog; unrecognized payload values are never returned.',
]
