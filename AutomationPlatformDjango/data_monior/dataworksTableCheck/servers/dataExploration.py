#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/9/14 16:59
# @Author : LiZongJie
# @Site : 
# @File : dataExploration.py
# @Software: PyCharm
'''
探查任务
1.必要参数：数据源、表名、字段名、字段类型、主键字段
2.任务步骤：
第一步：
表级校验：重复记录数、唯一主键数、表总数据量、主键全为空值数
第二步：
字段校验：字段空值数、唯一值数量、
第三步：根据字段类型分类 字符串字段(string)、数值字段(number)
字符串字段：最大长度、最小长度
数值字段：平均值、最小值、最大值
枚举值字段：(判断规则：唯一值数量<10 且 唯一值占比小于10%)
'''
from data_monior.dataworksTableCheck.servers.odpsSelectSql import GetDataWorksSql
from data_monior.dataworksTableCheck.servers.odpsSelect import *

getsql = GetDataWorksSql()


class dataExploration(object):
    def __init__(self, db_info):
        '''
        初始化
        :param project: 项目
        :param table:表名
        :param col:字段名
        :param colType:字段类型
        :param colKey:主键
        '''
        # self.project = project
        self.db_type = db_info['db_type']
        if self.db_type == 'azuresqlserver':
            server = db_info['db_host']
            database = db_info['db_name']
            self.o = Azure_Conn(server, database)
            # self.o = Odps_Con(user, password, project)
        else:
            self.o = ''

    def gettableinfo(self, table):
        '''
        获取表信息
        :return:
        '''
        sql = getsql.gettableinfo(table)
        result = self.o.select_sql_dict(sql)
        return result

    def gettablecolumnsinfo(self, table):
        '''
        获取表字段信息
        :param table:
        :return:
        '''
        sql = getsql.getcolumnsinfo(table)
        result = self.o.select_sql_dict(sql)
        columnsList = [i['column_name'] for i in result]
        return result, columnsList

    def repeatCheck(self, colList, table, term):
        '''
        重复数据校验/主键重复校验
        :param colList: 表所有字段/主键字段
        :param table: 表名
        :param term: 条件
        :return:
        '''
        colList = str(colList).replace('[', '').replace(']', '').replace("'", '')
        RepeatSql, detailsSql = getsql.getRepeatSql(colList, table, term)
        RepeatResult = self.o.select_sql_dict(RepeatSql)
        return RepeatResult, detailsSql

    def tableAllNum(self, table, term):
        '''
        表总数据量
        :param table: 表名
        :param term: 条件
        :return:
        '''
        AllNumSql = getsql.getTableAllNumSql(table, term)
        result = self.o.select_sql_dict(AllNumSql)
        return result

    def columnsNullCheck(self, column, table, term):
        '''
        字段空值率/唯一值统计
        :param column:字段名
        :param table:表名
        :param term:条件
        :return:
        '''
        columnnullsql = getsql.getColumnsNullRate(column, table, term)
        result = self.o.select_sql_dict(columnnullsql)
        return result, columnnullsql

    def enumsFiledCheck(self, column, table, term):
        '''
        枚举值字段校验
        :param column: 主键字段
        :param table: 表名
        :param term: 条件
        :return:
        '''
        EnumsSql = getsql.getEnumsFiledIndex(column, table, term)
        EnumsResult = self.o.select_sql_dict(EnumsSql)
        return EnumsResult, EnumsSql

    def stringFiledCheck(self, column, table, term):
        '''
        字符串类型字段 统计字段最大长度和最小长度
        :return: name(字段名),max_l,min_l
        '''
        stringSql = getsql.getStringFiledIndex(column, table, term)
        result = self.o.select_sql_dict(stringSql)
        return result, stringSql

    def NumberFiledCheck(self, column, table, term):
        '''
        数值类型字段 统计字段最大值、最小值、平均值
        :return: name(字段名),max_v,min_v,avg_v
        '''
        sql = getsql.getNumberFiledIndex(column, table, term)
        result = self.o.select_sql_dict(sql)
        return result, sql

    def sqlquery(self, sql):
        print(sql)
        result = self.o.select_sql_dict(sql)
        print(result)
        return result
