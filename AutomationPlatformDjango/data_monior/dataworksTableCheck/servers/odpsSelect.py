#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/7/23 10:43
# @Author : LiZongJie
# @Site : 
# @File : odps_select.py
# @Software: PyCharm
from odps import ODPS
import pyodbc
import pandas as pd
from dbutils.pooled_db import PooledDB
import warnings

warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class Odps_Con(ODPS):
    def select_sql(self, sql):
        for record in self.execute_sql(sql).open_reader():
            # result = dict(record)
            return record[0]

    def select_sql_dict(self, sql):
        instance = self.execute_sql(sql)
        self.df_db = instance.open_reader(tunnel=True, limit=False).to_pandas()
        self.result = self.df_db.to_dict(orient='records')
        return self.result


class Azure_Conn(object):
    def __init__(self, server, database):
        self.conn_pool(server, database)

    def conn_pool(self, server, database):
        '''
        创建连接池
        参数说明：
        1.creator：数据库驱动模块，如常见的pymysql,pymssql,cx_Oracle模块。无默认值
        2.mincached：初始化连接池时创建的连接数。默认为0，即初始化时不创建连接。(建议默认0，假如非0的话，在某些数据库不可用时，整个项目会启动不了)
        3.maxcached：池中空闲连接的最大数量。默认为0，即无最大数量限制。(建议默认)
        4.maxshared：池中共享连接的最大数量。默认为0，即每个连接都是专用的，不可共享(不常用，建议默认)
        5.maxconnections：被允许的最大连接数。默认为0，无最大数量限制。(视情况而定)
        6.blocking：连接数达到最大时，新连接是否可阻塞。默认False，即达到最大连接数时，再取新连接将会报错。(建议True，达到最大连接数时，新连接阻塞，等待连接数减少再连接)
        7.maxusage：连接的最大使用次数。默认0，即无使用次数限制。(建议默认)
        8.setsession：可选的SQL命令列表，可用于准备会话。(例如设置时区)
        9.reset：当连接返回到池中时，重置连接的方式。默认True，总是执行回滚。
        10.ping：确定何时使用ping()检查连接。默认1，即当连接被取走，做一次ping操作。0是从不ping，1是默认，2是当该连接创建游标时ping，4是执行sql语句时ping，7是总是ping
        :param server:
        :param DATABASE:
        :return:
        '''
        self.pool = PooledDB(pyodbc, blocking=True, DRIVER='ODBC Driver 17 for SQL Server',
                             maxconnections=5,
                             Server=server,
                             DATABASE=database,
                             Trusted_Connection='yes')
        # self.conn = pool.connection()

    def select_sql_dict(self, sql):
        conn = self.pool.connection()
        data = pd.read_sql(sql, conn)
        res = data.to_dict('records')
        return res

    def close(self):
        self.pool.close()
    # def select_table_columns(self):
    #     columnsList = [i['column_name'] for i in self.result]
    #     return columnsList
