def CaseSql1(case_name, case_type, prj_id, module_id, online_type, api_list, bd_id=''):
    if case_type == '':
        case_type = "'0', '1', '2'"
    elif case_type == '2':
        case_type = "'2'"
    elif case_type == '1':
        case_type = "'1'"
    elif case_type == '0':
        case_type = "'0'"
    elif case_type == '4':
        case_type = "'0', '1', '2','3'"
    if online_type == '':
        online_type = "'0','1'"
    elif online_type == '0':
        online_type = "'0'"
    elif online_type == '1':
        online_type = "'1'"
    prj_id = 'IS NOT NULL' if prj_id == '' else '={}'.format(prj_id)
    module_id = 'IS NOT NULL' if module_id == '' else '={}'.format(module_id)
    bd_id = '' if bd_id == '' else 'AND api_case.bd_id={}'.format(bd_id)
    # 查找用例列表数据
    sql = '''
           SELECT api_case.case_id,
           api_case.case_name,
           api_case.online_type,
           api_case.case_type,
           api_case.description,
           api_case.api_list,
           api_case.project_id,
           api_case.module_id,
           api_case.create_time,
           api_case.update_time,
           api_case.creator,
           api_project.prj_name,
           api_module.module_name,
           api_business.bd_name,
           api_business.bd_id,
           api_case.case_nums
           FROM api_case
           LEFT JOIN api_project ON api_case.project_id = api_project.prj_id
           LEFT JOIN api_module ON api_case.module_id = api_module.module_id
           LEFT JOIN api_business ON api_case.bd_id = api_business.bd_id
           WHERE api_case.case_name LIKE   '%{}%' 
           AND api_case.api_list LIKE   '%{}%' 
           AND api_case.project_id {} 
           AND api_case.module_id {}
           AND api_case.case_type in ({})
           AND api_case.online_type in ({})
           {}
           AND api_project.is_delete != '1'    
           AND api_module.is_delete != '1'
           AND api_case.is_delete != '1' ORDER BY api_case.update_time DESC
           '''.format(case_name, api_list, prj_id, module_id, case_type, online_type, bd_id)
    return sql


def sql2():
    """
    统计用例总数
    :return:
    """
    sql = """
    SELECT sum( case_nums ) FROM api_case WHERE is_delete = '0'
    """
    return sql


def sql3():
    """
    统计各个项目，用例数和接口数
    :return:
    """
    sql = """
    SELECT
		a.prj_id,
		a.prj_name,
		b.case_nums,
		e.api_nums 
	FROM
		api_project AS a
		LEFT JOIN ( SELECT project_id, sum( case_nums ) AS case_nums FROM api_case WHERE is_delete = '0' GROUP BY project_id ) b ON a.prj_id = b.project_id
		JOIN (
		SELECT
			c.prj_id,
			c.prj_name,
			d.api_nums 
		FROM
			api_project AS c
			LEFT JOIN ( SELECT project_id, COUNT( api_id ) AS api_nums FROM api_interface WHERE is_delete = '0' GROUP BY project_id ) AS d ON c.prj_id = d.project_id 
		WHERE
			is_delete = '0' 
		) AS e ON a.prj_id = e.prj_id 
	WHERE
		is_delete = '0' 
union 
SELECT NULL as prj_id, '合计' as prj_name, (sum(y.case_nums)) as case_nums,(sum(y.api_nums)) as api_nums
from (SELECT
		a.prj_id,
		a.prj_name,
		b.case_nums,
		e.api_nums 
	FROM
		api_project AS a
		LEFT JOIN ( SELECT project_id, sum( case_nums ) AS case_nums FROM api_case WHERE is_delete = '0' GROUP BY project_id ) b ON a.prj_id = b.project_id
		JOIN (
		SELECT
			c.prj_id,
			c.prj_name,
			d.api_nums 
		FROM
			api_project AS c
			LEFT JOIN ( SELECT project_id, COUNT( api_id ) AS api_nums FROM api_interface WHERE is_delete = '0' GROUP BY project_id ) AS d ON c.prj_id = d.project_id 
		WHERE
			is_delete = '0' 
		) AS e ON a.prj_id = e.prj_id 
	WHERE
		is_delete = '0' ) as y
    """
    return sql


def sql4():
    """
    项目数，接口数
    :return:
    """
    sql = """
    SELECT
        project_id,
        prj_name,
        module_id,
        module_name,
        api_url,
        api_list,
        case_nums,
        nums 
    FROM
        (
        SELECT
            a.project_id,
            d.prj_name,
            a.module_id,
            e.module_name,
            a.api_url,
            b.api_list,
            b.case_nums,
            ( sum( case_nums ) over ( PARTITION BY a.api_url ) ) AS nums 
        FROM
            api_interface AS a
            LEFT JOIN ( SELECT project_id, module_id, api_list, case_nums FROM api_case WHERE is_delete = '0' ) AS b ON a.project_id = b.project_id 
            AND a.module_id = b.module_id 
            AND a.api_url = b.api_list
            RIGHT JOIN api_project AS d ON a.project_id = d.prj_id
            RIGHT JOIN api_module AS e ON a.module_id = e.module_id 
        WHERE
            a.is_delete = '0' 
        ) AS c 
    GROUP BY
        project_id,
        prj_name,
        module_id,
        module_name,
        api_url,
        api_list,
        case_nums,
        nums 
    """
    return sql
