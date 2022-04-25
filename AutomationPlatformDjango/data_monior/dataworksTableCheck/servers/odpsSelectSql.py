#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/7/23 10:44
# @Author : LiZongJie
# @Site : 
# @File : odpsSelectSql.py
# @Software: PyCharm

class GetDataWorksSql(object):
    def __init__(self):
        pass

    def gettableinfo(self, table=None):
        if table is None:
            sql = '''
            SELECT
                distinct table_schema,table_name,concat('[',table_schema,'].[',table_name,']') schema_table
            FROM
                information_schema.TABLES 
           
            '''
        else:
            sql = '''
            SELECT    *
                FROM    information_schema.TABLES 
                where table_name='{table}'
            '''.format(table=table)
        return sql

    def getcolumnsinfo(self, table):
        sql = '''
        SELECT concat('[',column_name,']') column_name
        ,'' column_comment
         ,data_type
        FROM    information_schema.COLUMNS
        WHERE   table_name = '{table}'
        '''.format(table=table)
        return sql

    def getRepeatSql(self, columns, table, term):
        '''
        重复数据校验sql
        :param columns: 表字段
        :param table: 表名
        :param term: 条件
        :return:
        '''
        select = '''select count(1) as RepeatNum,{columns}'''.format(columns=columns)
        tablefrom = ''' from {table} '''.format(table=table)
        if len(term) > 0:
            where = ''' where {term} '''.format(term=term)
        else:
            where = ''
        group = ''' group by {columns}'''.format(columns=columns)
        having = ''' having count(1)>1 '''
        order_limit = '''order by count(1) desc limit 10 '''
        detailsSql = select + tablefrom + where + group + having + order_limit
        sql = 'select count(1) cnt from (' + select + tablefrom + where + group + having + ')'
        return sql, detailsSql

    def getColumnsNullRate(self, column, table, term):
        '''
        统计字段 空值和唯一值数量 sql
        :param column: 字段名
        :param table: 表名
        :param term: 条件
        :return:cnt_null(空值数),cnt_distinct(唯一值数量)
        '''
        select = ''' SELECT '{column}' as name ,sum(
                    case
                        when (cast({column} as string) is null or cast({column} as string)='') then 1
                        else 0
                    end
                ) as cnt_null,
                count(DISTINCT({column})) as cnt_distinct '''.format(column=column)
        tablefrom = ''' from {table}'''.format(table=table)
        if len(term) > 0:
            where = ''' where {term} '''.format(term=term)
        else:
            where = ''
        # where = ''' where {term}'''.format(term=term)
        sql = select + tablefrom + where
        return sql

    def getStringFiledIndex(self, column, table, term):
        '''
        获取字符串类型字段指标
        :param column: 字段名
        :param table: 表名
        :param term: 条件
        :return: max_l(最大长度),min_l(最小长度)
        '''
        select = '''
            SELECT
            '{column}' as name,
            max(nvl(LENGTH({column}),0)) as max_l,
            min(nvl(LENGTH({column}),0)) as min_l,
            0 as max_v,
            0 as min_v,
            0 as avg_v,
            '' as distinct_v
        '''.format(column=column)
        tablefrom = ''' from {table}'''.format(table=table)
        if len(term) > 0:
            where = ''' where {term} '''.format(term=term)
        else:
            where = ''
        # where = ''' where {term}'''.format(term=term)
        sql = select + tablefrom + where
        return sql

    def getNumberFiledIndex(self, column, table, term):
        '''
        获取数值类型指标维度
        :param column:
        :param table:
        :param term:
        :return:
        '''
        select = ''' select
            '{column}' as name,
            0 as max_l,
            0 as min_l,
            max({column}) as max_v,
            min({column}) as min_v,
            avg({column}) as avg_v,
            '' as distinct_v
        '''.format(column=column)
        tablefrom = ''' from {table}'''.format(table=table)
        if len(term) > 0:
            where = ''' where {term} '''.format(term=term)
        else:
            where = ''
        # where = ''' where {term}'''.format(term=term)
        sql = select + tablefrom + where
        return sql

    def getEnumsFiledIndex(self, column, table, term):
        '''
        获取枚举值类型指标维度
        :param column:
        :param table:
        :param term:
        :return:
        '''
        select = ''' select
            '{column}' as name,
            0 as max_l,
            0 as min_l,
            0 as max_v,
            0 as min_v,
            0 as avg_v,
            wm_concat(',', value) as distinct_v
        '''.format(column=column)
        subSelect = '''SELECT DISTINCT(cast({column} as STRING)) AS value '''.format(column=column)
        subFrom = ''' from {table}'''.format(table=table)
        if len(term) > 0:
            subwhere = ''' where {term} '''.format(term=term)
        else:
            subwhere = ''
        # subwhere = ''' where {term})'''.format(term=term)
        sql = select + 'from (' + subSelect + subFrom + subwhere + ' )'
        return sql

    def getTableAllNumSql(self, table, term):
        '''
        表总数据量sql
        :param table: 表名
        :param term: 条件
        :return:
        '''
        select = ''' select count(1) cnt'''
        tablefrom = ''' from {table}'''.format(table=table)
        if len(term) > 0:
            where = ''' where {term} '''.format(term=term)
        else:
            where = ''
        # where = ''' where {term}'''.format(term=term)
        sql = select + tablefrom + where
        return sql

    def columnsdatadetailsql(self, table, term):
        select = '''select * '''
        tablefrom = ''' from {table}'''.format(table=table)
        if len(term) > 0:
            where = ''' where {term} '''.format(term=term)
        else:
            where = ''

        sql = select + tablefrom + where +'limit 10'
        return sql

    def distinctdetailsql(self, table, term, column, allnum):
        select = f'''select {column} as 字段值,
                            count(1) as 数量,
                            CONCAT(ROUND(count(1)/{allnum}*100,2), '%') as 占比 '''
        tablefrom = f''' from {table}'''
        if len(term) > 0:
            where = f''' where {term} '''
        else:
            where = ''
        group = f''' group by {column}'''
        order_limit = ''' order by count(1) desc limit 30 '''
        sql = select + tablefrom + where + group + order_limit
        return sql
