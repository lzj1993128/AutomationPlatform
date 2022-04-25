#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/2 14:44
# @Author : LiZongJie
# @Site : 
# @File : monior_job.py
# @Software: PyCharm
import re
import datetime
import time
from data_monior.models import *
from api.models import *
from data_monior.data_monior import odps_conn
from data_monior.data_monior.thread_result import thread_result
from data_monior.data_monior.write_time import write_time
import logging

logger = logging.getLogger('log')


def date_time(date_format):
    '''
    时间参数化
    thedate：格式YYYYMMDD，当前日期的前一天
    thisdate：格式YYYY-MM-DD
    themoth：格式YYYYMM，当月
    thismoth：格式YYYY-MM
    :param date_format:
    :return:
    '''
    now_time = datetime.datetime.now()
    yes_time = now_time + datetime.timedelta(days=-1)
    if date_format == 'thedate':
        date = yes_time.strftime('%Y%m%d')
    elif date_format == 'thisdate':
        date = yes_time.strftime('%Y-%m-%d')
    elif date_format == 'themoth':
        date = yes_time.strftime('%Y%m')
    elif date_format == 'thismoth':
        date = yes_time.strftime('%Y-%m')
    return date


class Data_Monior(object):
    def get_all_sql(self):
        global rule_sql
        '''
        获取每天需要执行的sql，并参数化对应分区表达式
        :return:
        '''
        all_sql = Datamonior.objects.filter(is_delete=0, is_enable=0).values()
        # print(all_sql)
        check_all_sql = []
        for i in all_sql:
            try:
                # logger.info('调试'+i)
                check_sql = {}
                rule_sql = i['rule_sql']
                date_format = re.findall("{(.*?)}", rule_sql)
                for k in date_format:
                    date = date_time(k)
                    rule_sql = rule_sql.replace('{%s}' % (k), date)
                pt = re.findall("pt='(.*?)'", rule_sql)[0]
                check_sql['table'] = i['table']  # 表名
                check_sql['project'] = i['project']  # 所属项目
                check_sql['person'] = i['person']  # 负责人
                check_sql['person_phone'] = i['person_phone']  # 负责人手机号
                check_sql['rule_id'] = i['id']  # 规则id
                check_sql['run_date'] = time.strftime('%Y%m%d')  # 运行时间
                check_sql['check_way'] = i['check_way']  # 校验方式
                check_sql['compare_way'] = i['compare_way']  # 比较方式
                check_sql['check_type'] = i['check_type']  # 校验类型
                check_sql['sql'] = rule_sql
                check_sql['pt'] = pt
                check_sql['desired_value'] = i['desired_value']  # 预期值
                check_sql['rule_name'] = i['rule_name']  # 规则名字
                check_sql['level'] = i['level']  # 规则等级
                check_all_sql.append(check_sql)
            except Exception as f:
                print(f)
                continue
        print(check_all_sql)
        return check_all_sql

    def create_con(self):
        _data = Database.objects.filter(connect_name='数仓').values_list('db_type', 'db_host', 'db_user', 'db_passwd')
        persist = odps_conn.con_test_(_data[0][0], _data[0][1], _data[0][2], _data[0][3])  # 创建连接池
        return persist

    @write_time
    def run_check_sql(self, persist):
        logging.info('获取运行sql')
        check_all_sql = self.get_all_sql()
        logging.info('获取运行sql成功')
        # max_workers = len(check_all_sql)
        max_workers = 10
        logging.info('开启多线程执行sql')
        thread_result(persist, check_all_sql, max_workers=max_workers)
        # persist.close()
