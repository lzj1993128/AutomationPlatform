#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/3 16:23
# @Author : LiZongJie
# @Site : 
# @File : thread_result.py
# @Software: PyCharm

from concurrent.futures import ThreadPoolExecutor, as_completed
from data_monior.data_monior.odps_conn import db_con
from data_monior.models import Datamonior_History

import logging

logger = logging.getLogger('log')

def thread_result(persist, all_sql, max_workers=None):
    """
    创建线程池运行所有sql
    :param persist: 线程池
    :param all_sql: 所有sql
    :param max_workers: 最大线程数
    :return:
    """
    # print(max_workers)
    executor = ThreadPoolExecutor(max_workers=max_workers)  # 创建线程池
    result_all = []
    # 多线程执行sql
    all_task = [executor.submit(db_con(persist).select, sql) for sql in all_sql]
    # wait(all_task, return_when=ALL_COMPLETED)
    # 获取线程执行结果
    for future in as_completed(all_task):
        data = future.result()
        result_all.append(data)
        Datamonior_History.objects.create(rule_id=data.get('rule_id'),
                                          status=data.get('status'),
                                          run_result=data.get('result'),
                                          run_date=data.get('run_date'),
                                          pt=data.get('pt'),
                                          project=data.get('project'),
                                          table=data.get('table'),
                                          person=data.get('person'),
                                          person_phone=data.get('person_phone'),
                                          check_type=data.get('check_type'),
                                          rule_name=data.get('rule_name'),
                                          check_way=data.get('check_way'),
                                          compare_way=data.get('compare_way'),
                                          rule_sql=data.get('sql'),
                                          desired_value=data.get('desired_value'),
                                          level = data.get('level')
                                          )
        logger.info(str(data))
        print(data)
    return result_all
