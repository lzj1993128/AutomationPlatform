def IndexSql1(project_id):
    """
    统计接口数量
    :param project_id:
    :return:
    """
    sql = """
    SELECT
	count( a.api_id ) AS total_api_nums,
	count( CASE WHEN a.request_method = 'http' THEN 'api_http_nums' END ) AS api_http_nums,
	count( CASE WHEN a.request_method = 'dubbo' THEN 'api_dubbo_nums' END ) AS api_dubbo_nums 
    FROM
        api_interface a 
    WHERE
        a.is_delete = '0' and a.project_id = {}
    """.format(project_id)
    return sql


def IndexSql2(project_id):
    """
    统计用例数量
    :param project_id:
    :return:
    """
    sql = """
    SELECT
sum(case_nums) as total_case_nums,
	sum( CASE WHEN b.case_type = '0' THEN b.case_nums ELSE 0 END ) AS 'single_case',
	sum( CASE WHEN b.case_type = '2' THEN b.case_nums ELSE 0 END ) AS 'public_case' ,
	sum(case 'case_type' when '1' then case_nums else 0 end) as 'business_case'
FROM
	( SELECT case_type, sum( case_nums ) case_nums FROM api_case WHERE is_delete = '0' and project_id = {} GROUP BY case_type ) b

    """.format(project_id)
    return sql


def IndexSql3(project_id):
    """
    统计计划数量
    :param project:
    :return:
    """
    sql = """
    SELECT
	count( plan_id ) plan_nums 
FROM
	api_plan 
WHERE
	is_delete = '0' 
	AND project_id = {};
    
    """.format(project_id)
    return sql


def IndexSql4(project_id):
    """
    返回
    :param prject_id:
    :return:
    """
    sql = """
    SELECT
	count( task_id ) plan_run_times 
FROM
	plan_run_history 
WHERE
	is_delete = '0' 
	AND project_id = {}
    
    """.format(project_id)
    return sql
