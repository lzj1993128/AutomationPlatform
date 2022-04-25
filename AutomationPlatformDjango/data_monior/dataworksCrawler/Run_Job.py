#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/24 15:09
# @Author : LiZongJie
# @Site : 
# @File : run_job.py
# @Software: PyCharm

import time
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_monior.dataworksCrawler.server.GetQualityEntity import GetEntity
from data_monior.dataworksCrawler.server.ListQualityResultsByEntity import Result_Num
# from data_monior.dataworksTableCheck.servers.dataWorksApi import Sample
# from data_monior.dataworksCrawler.server.Run_Time import get_parameter
from data_monior.models import *
from odps import ODPS
from utils.PageUtil import PageUtil
from utils.DbUtil import DatabaseUtil
from django.db import close_old_connections
from data_monior.dataworksCrawler.server.Fuzzy_Match import project_fuzzy_match
import pandas as pd
from django.db import connections
import logging

logger = logging.getLogger('log')
owner_name = {
    '333503': '苏茂成', '188772': '陈樟涛', '322142': '张翔翔', '323251': '牛百阳', '323654': '杜康', '333541': '邵百川',
    '323653': '张敬超', '703240': '周龙', '702109': '李志远'
}
name_owner = dict([val, key] for key, val in owner_name.items())

project_name = {

}
pageUtil = PageUtil()


class run_job(object):
    def __init__(self, user, password):
        now_time = datetime.datetime.now()
        # now_time = now_time + datetime.timedelta(days=-2)
        yes_time = now_time + datetime.timedelta(days=-1)
        # print(now_time,yes_time)
        self.date = yes_time.strftime('%Y-%m-%d 00:00:00')  # 业务日期时间
        self.job_date = now_time.strftime('%Y-%m-%d')  # 调度时间
        self.api = Sample(user, password)
        close_old_connections()
        # self.job_date_last = yes_time.strftime('%Y-%m-%d')  # 当前时间前一天

    def rule_handle_list(self):
        '''
        获取最新条处理记录并且预期处理时间大于当前时间
        用于判断规则是否已处理
        :return:
        handle_list：取出预计处理时间在当前时间以后的ruleid
        handle_list_last：取出预计处理时间在当前时间前一天的ruleid
        '''
        # pageUtil = PageUtil()
        # # now_time = datetime.datetime.now()
        # # date = now_time.strftime('%Y-%m-%d')
        # handle_list = dataworks_rule_handle.objects.all()
        # handle = pageUtil.searchSqlFieldData(handle_list)
        # new_handle = pd.DataFrame(handle)
        pageUtil = PageUtil()
        # now_time = datetime.datetime.now()
        # date = now_time.strftime('%Y-%m-%d')
        handle_list = dataworks_rule_handle.objects.all()
        # sql = '''select * from data_monior_dataworks_rule_handle'''
        # handle_list = self.dbUtil.sql_to_dict(sql)
        # handle_list = dataworks_rule_handle.objects.all()
        # logger.error('rule_handle_list:%s' % (str(handle_list)))
        handle = pageUtil.searchSqlFieldData(handle_list)
        new_handle = pd.DataFrame(handle)
        if new_handle.empty:
            handle_list = []
            new_df = []
            handle_list_last = []
        else:
            max_conduct = new_handle.sort_values('conduct_time', ascending=False).groupby('ruleid',
                                                                                          as_index=False).first()
            new_df = max_conduct[(max_conduct.over_time > self.job_date) | (max_conduct.over_time == self.job_date)]
            handle_list = new_df.ruleid.values.tolist()  # 取出预计处理时间在当前时间以后的ruleid
            new_df_last = max_conduct[max_conduct.over_time == self.date[0:10]]
            handle_list_last = new_df_last.ruleid.values.tolist()  # 取出预计处理时间在当前时间前一天的ruleid
        # except Exception as f:
        #     logger.error('报错：%s' % (str(f)))
        #     handle_list = []
        #     new_df = []
        #     handle_list_last = []
        return handle_list, new_df, handle_list_last

    def get_create_owner_name(self, create_owner_id):
        try:
            create_owner_name = owner_name[create_owner_id]
        except:
            create_owner_name = '未知'
        return create_owner_name

    def get_all_table(self):
        user = 'LTAI4GHKZBiC7EPpCjuN1kNU'
        password = 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL'
        project = ['ncz_adm_dev', 'nczbigdata_dev', 'nczalgo_dev']  # 项目空间
        result = []
        for i in project:
            odps = ODPS(user, password, i)
            if i != 'nczalgo_dev':
                sql = '''SELECT  table_name,owner_name,table_comment
                        ,substr(table_schema,1,length(table_schema)-4) table_schema
                            FROM    information_schema.TABLES
                            WHERE   table_name not like '%_realtime%'
                            and table_name not like 'tmp%'
                            and table_name not like 'temp%'
                            and table_name not like 'viewdas%'
                            and  (table_comment IS not NULL OR table_comment <> '')
                            and (table_name like 'dwd%'
                            or table_name like 'dws%'
                            or table_name like 'rpt%'
                            or table_name like 'dm%'
                            or table_name like 'ods%'
                            or table_name like 'comp%')
                 '''
            else:
                sql = '''SELECT  table_name,owner_name,table_comment
                        ,substr(table_schema,1,length(table_schema)-4) table_schema
                            FROM    information_schema.TABLES
                            WHERE   table_name ='ads_new_erp_burypoint_monitor'
                 '''
            for record in odps.execute_sql(sql).open_reader():
                res = dict(record)
                result.append(res)
        return result

    def get_tables_id(self, tables):
        create_owner_id = tables['owner_name'][-6:]
        # tables['create_owner_id'] = create_owner_id
        tables['create_owner_name'] = self.get_create_owner_name(create_owner_id)  # 获取表创建者名字
        tables['data_model'] = tables['table_name'].split('_')[0]  # 表所属数仓分层
        tables['create_time'] = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')  # 获取数据时间
        tables['project'] = project_fuzzy_match(tables['table_name'])
        time.sleep(0.5)
        table_list = GetEntity.main(tables, name_owner,self.api)  # 获取表id
        return table_list

    def Thread_Reasult_Tables(self, tables):
        # handle_list, new_df, handle_list_last = self.rule_handle_list()
        result_dict = {
            'rulename': '', 'checkresult': '', 'runtime': '', 'bizdate': self.date, 'job_run_date': self.job_date,
            'ruleid': tables.get('table_id'), 'check_type': '', 'error_num': '', 'handle_status': '', 'overtime': ''
        }
        tables.update(result_dict)
        time.sleep(1)

        new_list = Result_Num.main(tables, self.date, self.date, self.handle_list, self.new_df,
                                   self.handle_list_last, self.api)  # 获取表规则结果列表
        return new_list

    # @get_parameter('获取分区表达式id')
    def run_job_twelve_time(self):
        '''
        每天晚上十二点全量获取覆盖表，所有表分区表达式id，存入数据库dataworks_alltables_rule
        '''
        # db='default'
        # print(settings.DATABASES)
        logger.info('连接数据库...')
        cursor = connections['default'].cursor()
        logger.info('清空data_monior_dataworks_alltables_rule...%s' % (str(cursor)))
        cursor.execute("TRUNCATE TABLE data_monior_dataworks_alltables_rule")
        # dataworks_alltables_rule.objects.all().delete()
        all_tables = self.get_all_table()
        all_table_list = []
        max_workers = 5
        executor = ThreadPoolExecutor(max_workers=max_workers)  # 创建线程池
        all_task = [executor.submit(self.get_tables_id, tables) for tables in all_tables]
        for future in as_completed(all_task):
            data = future.result()
            all_table_list.extend(data)
            print(len(all_table_list))
            print('result:' + str(data))
        product_list_to_insert = [
            dataworks_alltables_rule(table_schema=i['table_schema'], table_name=i['table_name'],
                                     owner_name=i['owner_name'], accountname=i['accountname'],
                                     create_owner_name=i['create_owner_name'], table_comment=i['table_comment'],
                                     table_id=i['table_id'], status=i['status'], description=i['description'],
                                     data_model=i['data_model'], create_time=i['create_time'], project=i['project'],
                                     accountnameid=i['accountnameid'])
            for i in all_table_list
        ]
        dataworks_alltables_rule.objects.bulk_create(product_list_to_insert)

    # @get_parameter('获取规则执行结果')
    def run_job_eight_thirty_time(self):
        '''
        每天早上8点30，获取所有规则运行情况，并存入数据库dataworks_alltables_rule_result
        '''
        self.handle_list, self.new_df, self.handle_list_last = self.rule_handle_list()
        all_tables = dataworks_alltables_rule.objects.filter(status=0).values()
        # data = pageUtil.searchSqlFieldData(all_tables)
        # print('1111111111',all_tables)
        all_table_list = []
        max_workers = 2
        executor = ThreadPoolExecutor(max_workers=max_workers)  # 创建线程池
        all_task = [executor.submit(self.Thread_Reasult_Tables, tables) for tables in all_tables]
        for future in as_completed(all_task):
            data = future.result()
            all_table_list.extend(data)
            logger.info(len(all_table_list))
            logger.info('result:' + str(data))
            # print(len(all_table_list))
            # print('result:' + str(data))
        product_list_to_insert = [
            dataworks_alltables_rule_result(table_schema=i['table_schema'], table_name=i['table_name'],
                                            owner_name=i['owner_name'], accountname=i['accountname'],
                                            create_owner_name=i['create_owner_name'], table_comment=i['table_comment'],
                                            table_id=i['table_id'], status=i['status'], description=i['description'],
                                            data_model=i['data_model'], rulename=i['rulename'],
                                            checkresult=i['checkresult'], runtime=i['runtime'], bizdate=i['bizdate'],
                                            job_run_date=i['job_run_date'], ruleid=i['ruleid'], project=i['project'],
                                            check_type=i['check_type'], error_num=i['error_num'],
                                            handle_status=i['handle_status'], over_time=i['overtime'],
                                            accountnameid=i['accountnameid'])
            for i in all_table_list
        ]
        dataworks_alltables_rule_result.objects.bulk_create(product_list_to_insert)
        logger.info('任务结束')
