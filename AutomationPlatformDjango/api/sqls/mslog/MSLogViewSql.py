def MSLogSql(ms_name):
    sql = '''SELECT api_mslog.*,api_project.prj_name,api_module.module_name 
               FROM api_mslog 
               LEFT JOIN api_project ON api_mslog.project_id = api_project.prj_id
               LEFT JOIN api_module ON api_mslog.module_id = api_module.module_id
               WHERE api_mslog.ms_name LIKE '%{}%' 
               AND api_project.is_delete != '1' 
               AND api_module.is_delete != '1'
               AND api_mslog.is_delete != '1' ORDER BY api_mslog.update_time DESC '''.format(ms_name)
    return sql
