def ProjectSql1(prj_name=''):
    sql = '''
    SELECT a.prj_id, a.prj_name, a.robot_group_id, a.description, a.create_time, a.update_time,config_robot.group_name
           FROM api_project as a
           LEFT JOIN config_robot ON a.robot_group_id = config_robot.robot_id
           WHERE a.prj_name like '%{}%'
           AND a.is_delete != '1' ORDER BY a.update_time DESC
    '''.format(prj_name)
    return sql