def bigDataSearchSql(big_data_name, prj_id, module_id):
    """
    大数据搜索语句
    :param prj_id:
    :param module_id:
    :return:
    """
    prj_id = 'IS NOT NULL' if prj_id == '' else '={}'.format(prj_id)
    module_id = 'IS NOT NULL' if module_id == '' else '={}'.format(module_id)
    sql = '''SELECT 
                big_data_bigdata.big_data_id,
                big_data_bigdata.big_data_name,
                big_data_bigdata.project_id,
                big_data_bigdata.module_id,
                big_data_bigdata.db_id,
                big_data_bigdata.requestCompareFieldList,
                big_data_bigdata.request_method,
                big_data_bigdata.api_name,
                big_data_bigdata.api_url,
                big_data_bigdata.method,
                big_data_bigdata.data_type,
                big_data_bigdata.requestHeader,
                big_data_bigdata.requestBody,
                big_data_bigdata.zk_database,
                big_data_bigdata.zk_api_name,
                big_data_bigdata.zk_api_method,
                big_data_bigdata.requestJson,
                big_data_bigdata.reponse_field,
                big_data_bigdata.report_database_name,
                big_data_bigdata.sql,
                big_data_bigdata.description,
                big_data_bigdata.creator,
                big_data_bigdata.last_updata_person,
                big_data_bigdata.create_time,
                big_data_bigdata.update_time,
                api_project.prj_name,
                api_module.module_name,
                api_database.db_host
               FROM big_data_bigdata 
               LEFT JOIN api_project ON big_data_bigdata.project_id = api_project.prj_id 
               LEFT JOIN api_module ON big_data_bigdata.module_id = api_module.module_id
               LEFT JOIN api_database ON big_data_bigdata.db_id = api_database.db_id
               WHERE big_data_bigdata.big_data_name LIKE '%{}%'
               AND big_data_bigdata.project_id {}
               AND big_data_bigdata.module_id {}
               AND api_project.is_delete != '1'
               AND api_module.is_delete != '1'
               AND big_data_bigdata.is_delete != 1 ORDER BY big_data_bigdata.update_time DESC '''.format(big_data_name, prj_id,
                                                                                                     module_id)
    return sql
