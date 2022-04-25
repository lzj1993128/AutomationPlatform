#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/10 9:59
# @Author : LiZongJie
# @Site : 
# @File : write_time.py
# @Software: PyCharm
import datetime,time
from data_monior.models import *

def write_time(func):
    def w_time(*args, **kwargs):
        start_time = datetime.datetime.now()  # 开始时间
        run_date = time.strftime('%Y%m%d')  # 运行日期
        func(*args, **kwargs)
        end_time = datetime.datetime.now()  # 结束时间
        delta = end_time - start_time
        delta_gmtime = time.gmtime(delta.total_seconds())
        duration_str = time.strftime("%H:%M:%S", delta_gmtime)
        run_log.objects.create(run_date=run_date,
                                          st_time=start_time,
                                          end_time=end_time,
                                          run_time=duration_str
                                          )
    return w_time