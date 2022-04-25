#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/3 16:02
# @Author : LiZongJie
# @Site : 
# @File : odps_conn.py
# @Software: PyCharm

from dbutils.pooled_db import PooledDB
import jaydebeapi
import os

driver_dict = {'odps': 'com.aliyun.odps.jdbc.OdpsDriver'}


def con_test_(db_type, url, user, password):
    """
    创建连接池persist，不同数据库类型需添加jarFile驱动
    例如：odps数据库 jarFile:odps-jdbc-3.2.2-jar-with-dependencies.jar
                    driver:com.aliyun.odps.jdbc.OdpsDriver
        file_name：列表中添加驱动文件名，并将驱动放在db_jdbc文件夹里
        driver_dict：字典中添加需要连接的数据库类型jdbc
    :param driver: 区分数据库类型
    :param url: 数据库地址
    :param user: 账号
    :param password:密码
    """
    jarFile = []
    path = os.getcwd()
    path = os.path.join(path, 'data_monior')
    path = os.path.join(path, 'db_jdbc')
    file_name = ['odps-jdbc-3.2.2-jar-with-dependencies.jar']
    for i in file_name:
        jarFile.append(os.path.join(path, i))
    driver = driver_dict[db_type]
    persist = PooledDB(creator=jaydebeapi, jclassname=driver, url=url,
                       driver_args=[user, password], jars=jarFile)
    return persist


def result_check(compare, desired, result):
    if compare == '=':
        if desired == result:
            status = 0
        else:
            status = 1
    if compare == '<':
        if result < desired:
            status = 0
        else:
            status = 1
    if compare == '>':
        if result > desired:
            status = 0
        else:
            status = 1
    return status


class db_con:
    def __init__(self, persist):
        self.conn = persist.connection()
        self.curs = self.conn.cursor()

    def select(self, sql):
        # print(sql)
        excute_sql = sql.get('sql')
        try:
            self.curs.execute(excute_sql)  # 操作数据库
            all = self.curs.fetchall()  # 查看全部数据
            sql['result'] = all[0][0]
            status = result_check(sql.get('compare_way'), sql.get('desired_value'), all[0][0])
            sql['status'] = status
        except Exception as f:
            sql['result'] = 0
            sql['status'] = 2
            sql['error'] = str(f)
        return sql

    def close(self):
        if self.conn:
            self.conn.close()
        if self.curs:
            self.curs.close()
