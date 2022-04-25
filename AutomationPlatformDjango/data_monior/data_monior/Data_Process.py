#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/8 10:54
# @Author : LiZongJie
# @Site : 
# @File : dayfor7.py
# @Software: PyCharm
import datetime
import pandas as pd


def get_time():
    '''
    生成时间列表
    '''
    # 生成本日时间列表
    i = datetime.datetime.now()
    today = datetime.date.today()
    date = [str(hour).zfill(2) + ':00' for hour in range(0, i.hour + 1)]
    date_time = [str(today) + ' ' + str(hour).zfill(2) for hour in range(0, i.hour + 1)]
    # 生成本周时间列表
    allweek = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    nowweek = i.weekday()
    week = allweek[nowweek:] + allweek[0:nowweek]
    week_time = [str((today - datetime.timedelta(days=8 - w)).strftime("%Y-%m-%d")) for w in range(2, 9)]
    # 生成本月时间列表
    month = i.strftime('%Y-%m-')
    day = [str(d) + '号' for d in range(1, i.day)]
    day_time = [month + str(d).zfill(2) for d in range(1, i.day)]
    return {'date': date, 'date_time': date_time, 'week': week, 'week_time': week_time, 'day': day,
            'day_time': day_time}


class Data_Process(object):
    def data_linechart(self, result_):
        result_dict = {}
        if len(result_) != 0:
            df = pd.DataFrame(result_)
            table_schema = list(set(df['table_schema'].values.tolist()))
            daylist = get_time().get('week_time')
            for i in table_schema:
                new_df = df[df.table_schema == i]
                # print(new_df)
                normal = [0 for index in range(7)]
                orange_alarm = [0 for index in range(7)]
                red_alarm = [0 for index in range(7)]
                no_run_rule = [0 for index in range(7)]
                error_request = [0 for index in range(7)]
                new_dict = {}
                for index, row in new_df.iterrows():
                    # print(row)
                    run_date = row.get('job_run_date')
                    if run_date in daylist:
                        day_index = daylist.index(run_date)
                        normal[day_index] = row.get('normal')
                        orange_alarm[day_index] = row.get('orange_alarm')
                        red_alarm[day_index] = row.get('red_alarm')
                        no_run_rule[day_index] = row.get('no_run_rule')
                        error_request[day_index] = row.get('error_request')
                new_dict['daytime'] = daylist
                new_dict['normal'] = normal
                new_dict['orange_alarm'] = orange_alarm
                new_dict['red_alarm'] = red_alarm
                new_dict['no_run_rule'] = no_run_rule
                new_dict['error_request'] = error_request
                result_dict[i] = new_dict
        return result_dict

    def data_piechart(self, result_, pro_dict):
        new_dict = {}
        for i in result_:
            old_dict = {}
            old_dict['space'] = i['table_schema']
            old_dict['own'] = pro_dict[i['table_schema']]
            result = [{'value': i['not_rule_table'], 'name': '不存在规则表'},
                      {'value': i['have_rule_table'], 'name': '存在规则表'}]
            old_dict['result'] = result
            new_dict[i['table_schema']] = old_dict
        return new_dict

    def dataworks_category(self, result):
        df = pd.DataFrame(result)
        table_schema = list(set(df['category'].values.tolist()))
        new_dict = {}
        for i in table_schema:
            new_df = df[df.category == i].to_dict('records')
            new_dict[i] = new_df
            # print(new_dict)
        return new_dict

    def data_SingleRuleRunHistory(self, result_):
        daylist = get_time().get('week_time')
        result = {}
        run_result_list = [0 for index in range(7)]
        for i in result_:
            run_date = i.get('run_date')
            if run_date in daylist:
                day_index = daylist.index(run_date)
                run_result_list[day_index] = i.get('run_result')
        result['daytime'] = daylist
        result['run_result_list'] = run_result_list
        return result

    def data_sql(self):
        sql = '''select table_schema,job_run_date,
                count( CASE WHEN checkresult = 0 and status=0 THEN 1 END ) normal,
                count( CASE WHEN checkresult = 1 and status=0 THEN 1 END ) orange_alarm,
                count( CASE WHEN checkresult = 2 and status=0 THEN 1 END ) red_alarm, 
                count( CASE WHEN checkresult = 3 and status=0 THEN 1 END ) no_run_rule,
                count( CASE WHEN checkresult = -2 and status=0 THEN 1 END ) rule_error,
                count( CASE WHEN checkresult = 4 or status=1  then 1 end ) error_request
                from (
                select 
            b.checkresult,b.check_type,b.ruleid,b.table_schema,b.job_run_date,a.status,b.status resultbyentity
            from data_monior_dataworks_alltables_rule a 
                left join(select * from data_monior_dataworks_alltables_rule_result)  b on a.table_id=b.table_id 
								where b.table_schema<>'') a 
            group by job_run_date,table_schema order by job_run_date desc
        '''
        return sql

    def data_sql2(self, rule_id):
        sql = '''
                      SELECT
                    job_run_date run_date,
	                cast( error_num AS SIGNED ) run_result  
                FROM
                    data_monior_dataworks_alltables_rule_result 
                WHERE
                    ruleid = {rule_id}
                order by job_run_date desc
                LIMIT 7
        '''.format(rule_id=rule_id)
        return sql

    def data_sql3(self):
        sql = '''SELECT
            table_schema,
            count( CASE WHEN `status` = 2 THEN 1 END ) not_rule_table,
            count( CASE WHEN `status` = 0 THEN 1 END ) have_rule_table 
            FROM
            data_monior_dataworks_alltables_rule 
            GROUP BY
            table_schema
        '''
        return sql

    def data_sql4(self, run_date, table_schema):
        sql = '''
                    select 'project' category,project,
                count(distinct table_name) all_table_num,
                count(distinct case when a.status=0 then table_name end) table_rule_num,
                count(case when a.status=0 then ruleid end) all_rule_num, 
                count( CASE WHEN checkresult = 0 and status=0 THEN 1 END ) normal,
                count( CASE WHEN checkresult = 1 and status=0 THEN 1 END ) orange_alarm,
                count( CASE WHEN checkresult = 2 and status=0 THEN 1 END ) red_alarm, 
                count( CASE WHEN checkresult = 3 and status=0 THEN 1 END ) no_run_rule,
                count( CASE WHEN checkresult = -2 and status=0 THEN 1 END ) rule_error,
                count( CASE WHEN checkresult = 4 or status=1  then 1 end ) error_request,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=0  then 1 end ) undisposed,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=1  then 1 end ) disposed
                from (
                select 
            a.*,b.checkresult,b.check_type,b.ruleid,b.status resultbyentity,handle_status
            from data_monior_dataworks_alltables_rule a 
                left join(select * from data_monior_dataworks_alltables_rule_result 
                where job_run_date='{run_date}')  b on a.table_id=b.table_id where a.table_schema = '{table_schema}') a 
            where data_model='rpt'
            group by project
            UNION all
            select 'create_owner_name' category,create_owner_name,
                count(distinct table_name) all_table_num,
                count(distinct case when a.status=0 then table_name end) table_rule_num,
                count(case when a.status=0 then ruleid end) all_rule_num, 
                count( CASE WHEN checkresult = 0 and status=0 THEN 1 END ) normal,
                count( CASE WHEN checkresult = 1 and status=0 THEN 1 END ) orange_alarm,
                count( CASE WHEN checkresult = 2 and status=0 THEN 1 END ) red_alarm, 
                count( CASE WHEN checkresult = 3 and status=0 THEN 1 END ) no_run_rule,
                count( CASE WHEN checkresult = -2 and status=0 THEN 1 END ) rule_error,
                count( CASE WHEN checkresult = 4 or status=1  then 1 end ) error_request,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=0  then 1 end ) undisposed,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=1  then 1 end ) disposed
                from (
                select 
            a.*,b.checkresult,b.check_type,b.ruleid,b.status resultbyentity,handle_status
            from data_monior_dataworks_alltables_rule a 
                left join(select * from data_monior_dataworks_alltables_rule_result 
                where job_run_date='{run_date}')  b on a.table_id=b.table_id where a.table_schema = '{table_schema}') a 
            group by create_owner_name
            UNION all
            select 'data_region' category,project,
                count(distinct table_name) all_table_num,
                count(distinct case when a.status=0 then table_name end) table_rule_num,
                count(case when a.status=0 then ruleid end) all_rule_num, 
                count( CASE WHEN checkresult = 0 and status=0 THEN 1 END ) normal,
                count( CASE WHEN checkresult = 1 and status=0 THEN 1 END ) orange_alarm,
                count( CASE WHEN checkresult = 2 and status=0 THEN 1 END ) red_alarm, 
                count( CASE WHEN checkresult = 3 and status=0 THEN 1 END ) no_run_rule,
                count( CASE WHEN checkresult = -2 and status=0 THEN 1 END ) rule_error,
                count( CASE WHEN checkresult = 4 or status=1  then 1 end ) error_request,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=0  then 1 end ) undisposed,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=1  then 1 end ) disposed
                from (
                select 
            a.*,b.checkresult,b.check_type,b.ruleid,b.status resultbyentity,handle_status
            from data_monior_dataworks_alltables_rule a 
                left join(select * from data_monior_dataworks_alltables_rule_result 
                where job_run_date='{run_date}')  b on a.table_id=b.table_id where a.table_schema = '{table_schema}') a 
                where data_model in ('dwd','dws','dm')
            group by project
            UNION all
            select 'check_type' category,check_type,
                count(distinct table_name) all_table_num,
                count(distinct case when a.status=0 then table_name end) table_rule_num,
                count(case when a.status=0 then ruleid end) all_rule_num, 
                count( CASE WHEN checkresult = 0 and status=0 THEN 1 END ) normal,
                count( CASE WHEN checkresult = 1 and status=0 THEN 1 END ) orange_alarm,
                count( CASE WHEN checkresult = 2 and status=0 THEN 1 END ) red_alarm, 
                count( CASE WHEN checkresult = 3 and status=0 THEN 1 END ) no_run_rule,
                count( CASE WHEN checkresult = -2 and status=0 THEN 1 END ) rule_error,
                count( CASE WHEN checkresult = 4 or status=1  then 1 end ) error_request,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=0  then 1 end ) undisposed,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=1  then 1 end ) disposed
                from (
                select 
            a.*,b.checkresult,b.check_type,b.ruleid,b.status resultbyentity,handle_status
            from data_monior_dataworks_alltables_rule a 
                left join(select * from data_monior_dataworks_alltables_rule_result 
                where job_run_date='{run_date}' )  b on a.table_id=b.table_id where  a.`status`=0 and
                 b.`status`=0  and b.checkresult <>3 and a.table_schema = '{table_schema}') a 
            group by check_type
            UNION all
            select table_schema category,
                table_schema,
                count(distinct table_name) all_table_num,
                count(distinct case when a.status=0 then table_name end) table_rule_num,
                count(case when a.status=0 then ruleid end) all_rule_num, 
                count( CASE WHEN checkresult = 0 and status=0 THEN 1 END ) normal,
                count( CASE WHEN checkresult = 1 and status=0 THEN 1 END ) orange_alarm,
                count( CASE WHEN checkresult = 2 and status=0 THEN 1 END ) red_alarm, 
                count( CASE WHEN checkresult = 3 and status=0 THEN 1 END ) no_run_rule,
                count( CASE WHEN checkresult = -2 and status=0 THEN 1 END ) rule_error,
                count( CASE WHEN checkresult = 4 or status=1  then 1 end ) error_request,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=0  then 1 end ) undisposed,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=1  then 1 end ) disposed
                from (
                select 
            a.*,b.checkresult,b.check_type,b.ruleid,b.status resultbyentity,handle_status
            from data_monior_dataworks_alltables_rule a 
                left join(select * from data_monior_dataworks_alltables_rule_result 
                where job_run_date='{run_date}')  b on a.table_id=b.table_id ) a 
            group by table_schema
            UNION all
            select 'source' category,project,
                count(distinct table_name) all_table_num,
                count(distinct case when a.status=0 then table_name end) table_rule_num,
                count(case when a.status=0 then ruleid end) all_rule_num, 
                count( CASE WHEN checkresult = 0 and status=0 THEN 1 END ) normal,
                count( CASE WHEN checkresult = 1 and status=0 THEN 1 END ) orange_alarm,
                count( CASE WHEN checkresult = 2 and status=0 THEN 1 END ) red_alarm, 
                count( CASE WHEN checkresult = 3 and status=0 THEN 1 END ) no_run_rule,
                count( CASE WHEN checkresult = -2 and status=0 THEN 1 END ) rule_error,
                count( CASE WHEN checkresult = 4 or status=1  then 1 end ) error_request,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=0  then 1 end ) undisposed,
                count( CASE WHEN checkresult <>0 and status=0 and handle_status=1  then 1 end ) disposed
                from (
                select 
            a.*,b.checkresult,b.check_type,b.ruleid,b.status resultbyentity,handle_status
            from data_monior_dataworks_alltables_rule a 
                left join(select * from data_monior_dataworks_alltables_rule_result 
                where job_run_date='{run_date}')  b on a.table_id=b.table_id where a.table_schema = '{table_schema}') a 
            where data_model='ods'
            group by project
            '''.format(run_date=run_date, table_schema=table_schema)
        return sql
