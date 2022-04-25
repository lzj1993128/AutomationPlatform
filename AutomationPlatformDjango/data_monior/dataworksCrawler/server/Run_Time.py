#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/29 16:00
# @Author : LiZongJie
# @Site : 
# @File : Run_Time.py
# @Software: PyCharm
import datetime, time
from data_monior.models import run_log


def get_parameter(name=None):
    def write_time(func):
        def w_time(*args, **kwargs):
            start_time = datetime.datetime.now()  # 开始时间
            run_date = time.strftime('%Y%m%d')  # 运行日期
            print(name + ':' + str(start_time))
            func(*args, **kwargs)
            res = '成功'
            end_time = datetime.datetime.now()  # 结束时间
            print(end_time)
            delta = end_time - start_time
            delta_gmtime = time.gmtime(delta.total_seconds())
            duration_str = time.strftime("%H:%M:%S", delta_gmtime)
            print(duration_str)
            run_log.objects.create(job_name=name, run_date=run_date,
                                   st_time=start_time,
                                   end_time=end_time,
                                   run_time=duration_str,
                                   res=res
                                   )

        return w_time

    return write_time
