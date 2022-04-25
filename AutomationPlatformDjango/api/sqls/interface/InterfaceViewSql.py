def InterfaceSql1(api_name, api_url, method, prj_id, module_id, requestMethod):
    # 查找接口列表数据
    prj_id = 'IS NOT NULL' if prj_id == '' else '={}'.format(prj_id)
    module_id = 'IS NOT NULL' if module_id == '' else '={}'.format(module_id)
    sql = '''SELECT api_interface.*,api_project.prj_name,api_module.module_name,d.case_nums
           FROM api_interface 
           LEFT JOIN api_project ON api_interface.project_id = api_project.prj_id 
           LEFT JOIN api_module ON api_interface.module_id = api_module.module_id 
           LEFT JOIN (SELECT api_list,sum(case_nums) as case_nums  from api_case where is_delete = '0' group by api_list ) as d on api_interface.api_url = d.api_list
           WHERE api_interface.api_name LIKE '%{}%'
           AND api_interface.api_url LIKE '%{}%' 
           AND api_interface.request_method  LIKE '%{}%'
           AND api_interface.method  LIKE '%{}%'
           AND api_interface.project_id {}
           AND api_interface.module_id {}
           AND api_project.is_delete != '1'
           AND api_module.is_delete != '1'
           AND api_interface.is_delete != '1' ORDER BY api_interface.update_time DESC '''.format(api_name, api_url,
                                                                                                 requestMethod, method,
                                                                                                 prj_id, module_id)
    return sql


def InterfaceSql2(api_id):
    sql = '''
    SELECT api_interface.*,api_project.prj_name,api_module.module_name 
           FROM api_interface 
           LEFT JOIN api_project ON api_interface.project_id = api_project.prj_id 
           LEFT JOIN api_module ON api_interface.module_id = api_module.module_id 
           WHERE api_id={}
           AND api_interface.is_delete != '1' ORDER BY api_interface.update_time DESC
    '''.format(api_id)
    return sql