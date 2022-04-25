#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/14 15:43
# @Author : LiZongJie
# @Site : 
# @File : columnsdetails.py
# @Software: PyCharm
from data_monior.dataworksTableCheck.servers.odpsSelectSql import GetDataWorksSql
from data_monior.dataworksTableCheck.servers.dataExploration import dataExploration


class detailscheck(object):
    def __init__(self, requestData, user, password):
        tablelambda = lambda source, table, environment: [source + '_dev.' + table, source + '.' + table][
            environment == 0]
        self.table = tablelambda(requestData['source'], requestData['table'], requestData['environment'])
        self.num = requestData['num']
        self.column = requestData['column']
        self.columntype = requestData['type']
        self.where = requestData['where']
        self.allnum = requestData['tableallnum']
        self.odps = dataExploration(user, password, requestData['source'] + '_dev')

    def wherehandle(self):
        where = ''
        if self.columntype == 'columnnull':
            wherecolumn = '''(cast({column} as string) is null or cast({column} as string)='') '''.format(column=self.column)
        elif self.columntype in ('max_l', 'min_l'):
            wherecolumn = ''' length({column}) ={num}'''.format(column=self.column, num=self.num)
        elif self.columntype in ('max_v', 'min_v'):
            wherecolumn = ''' {column}={num}'''.format(column=self.column, num=self.num)
        try:
            self.where.append(wherecolumn)
        except:
            pass
        for i in range(len(self.where)):
            y = self.where[i]
            if i + 1 == len(self.where):
                where += y
            else:
                where += (y + ' and ')
        return where

    def detailsdata(self):
        where = self.wherehandle()
        if self.columntype == 'cnt_distinct':
            sql = GetDataWorksSql().distinctdetailsql(self.table, where, self.column, self.allnum)
        else:
            sql = GetDataWorksSql().columnsdatadetailsql(self.table, where)
        print(sql)
        result = self.odps.sqlquery(sql)
        return result,sql
