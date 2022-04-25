#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/9/27 11:38
# @Author : LiZongJie
# @Site : 
# @File : dataCheck.py
# @Software: PyCharm

from concurrent.futures import ThreadPoolExecutor, as_completed
from data_monior.models import *
from data_monior.dataworksTableCheck.servers.dataExploration import dataExploration
# from data_monior.dataworksTableCheck.servers.dataWorksApi import Sample
import logging
import time, hashlib
import datetime

logger = logging.getLogger('log')


class fieldProbeJob(object):
    def __init__(self, db_info, environment, environmentdes):
        '''
        初始化连接ODPS数据库,odps只能连接开发环境所有空间必须加dev
        :param project: 所属空间
        :param environment: 环境code
        :param environmentdes: 环境中文名
        '''
        self.user = ''
        self.password = ''
        self.project = ''  #
        self.environment = environment
        self.environmentdes = environmentdes
        self.odps = dataExploration(db_info)
        # self.requests = Sample(self.user, self.password)
        # self.ownerdict = self.requests.getProjectsOwner(project)
        # projectiddict = requests.getProjects()
        # project_id = project['project']

    def create_id(self):
        m = hashlib.md5(str(time.clock()).encode('utf-8'))
        return m.hexdigest()

    def threadjob(self, tablecolumn):
        '''
        类型字段判断并获取结果
        :param tablecolumn:字段信息
        :return:
        '''
        column = tablecolumn['column_name']
        logger.info('[taskid:{}],探查字段信息：{}'.format(self.taskId, column))
        column_comment = tablecolumn['column_comment']
        data_type = tablecolumn['data_type']
        columnnull, columnnullsql = self.odps.columnsNullCheck(column, self.table, self.term)
        if columnnull[0]['cnt_distinct'] < 20 and columnnull[0]['cnt_distinct'] / self.tableallnum[0]['cnt'] < 0.1:
            res, Sql = self.odps.enumsFiledCheck(column, self.table, self.term)
            res[0]['type'] = 'enums'
            res[0]['typedes'] = '枚举值类型'
            # return res, Sql
        elif data_type in ('string'):
            res, Sql = self.odps.stringFiledCheck(column, self.table, self.term)
            res[0]['type'] = 'string'
            res[0]['typedes'] = '字符串类型'
            # return res, Sql
        elif data_type in ('datetime', 'timestamp'):
            res, Sql = self.odps.stringFiledCheck(column, self.table, self.term)
            res[0]['type'] = 'datetime'
            res[0]['typedes'] = '时间类型'
            # return res, Sql
        else:
            res, Sql = self.odps.NumberFiledCheck(column, self.table, self.term)
            res[0]['type'] = 'number'
            res[0]['typedes'] = '数值类型'
        res[0]['columnnull'] = columnnull[0]['cnt_null']
        res[0]['comment'] = column_comment
        res[0]['sql'] = columnnullsql + Sql
        # res[0]['table'] = self.table
        res[0]['taskId'] = self.taskId
        res[0]['cnt_distinct'] = columnnull[0]['cnt_distinct']
        return res[0]

    def checkJob(self, table, where, pk, columnsList, columnsInfo, id):
        '''
        校验任务
        :param table: 表名
        :param where: 条件
        :param pk: 主键
        :param columnsList: 字段列表
        :param columnsInfo: 字段信息
        :param id: 表id
        :return:
        '''
        self.table = table
        self.term = where
        self.taskId = self.create_id()
        logger.info('[taskid:{}],开始探查表:{}'.format(self.taskId, self.table.split('.')[1]))
        logger.info('[taskid:{}],探查表重复数据'.format(self.taskId))
        RepeatResult, detailsSql = self.odps.repeatCheck(columnsList, self.table, self.term)
        logger.info('[taskid:{}],探查表主键重复数据'.format(self.taskId))
        pkRepeatResult, pkDetailsSql = self.odps.repeatCheck(pk, self.table, self.term)
        self.tableallnum = self.odps.tableAllNum(self.table, self.term)
        # 获取 LastDdlTime(最近一次变更表结构的时间)、LastModifyTime(最近一次更新表的时间)、CreateTime(创建表的时间)、LifeCycle(表的生命周期。单位为天)
        logger.info('[taskid:{}],探查表信息'.format(self.taskId))
        # result = self.requests.getTableBasicInfo(self.table)
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S')
        # print('获取完成' + str(result)) primaryKeyList  'pkRepeatResult': pkRepeatResult[0]['cnt'],'pkDetailsSql': pkDetailsSql
        tableinfo = {'environment': self.environment, 'environmentdes': self.environmentdes,
                     'source': self.project, 'majorkey': pk, 'taskId': self.taskId, 'tableId_id': id,
                     'probeTime': nowtime, 'where': where.split(' and '),
                     'table': self.table.split('.')[1],
                     'owner': '', 'lifeCycle': '',
                     'createTime': '', 'tableallnum': self.tableallnum[0]['cnt'],
                     'repeatResult': RepeatResult[0]['cnt'], 'pkRepeatResult': pkRepeatResult[0]['cnt'],
                     'pkDetailsSql': pkDetailsSql,
                     'repeatDetailsSql': detailsSql, 'table_comment': '', 'dataSize': ''}
        dataExploration_RuleTable.objects.filter(id=id).update(LastProbeTime=nowtime)
        # dataExploration_TableHistory.objects.create(**tableinfo)
        resList = []
        if self.tableallnum[0]['cnt'] != 0:
            max_workers = 5
            executor = ThreadPoolExecutor(max_workers=max_workers)  # 创建线程池
            all_task = [executor.submit(self.threadjob, tablecolumn) for tablecolumn in columnsInfo]
            for future in as_completed(all_task):
                data = future.result()
                dataExploration_TableColumnsHistory.objects.create(**data)
                resList.append(data)
        return tableinfo, resList


class datacheck(object):
    def __init__(self, db_info, environment, environmentdes):
        # self.source = source
        self.environment = environment
        self.environmentdes = environmentdes
        self.Probejob = fieldProbeJob(db_info, self.environment, self.environmentdes)

    def wherelistcond(self, wherelist):
        x = ''
        for i in range(len(wherelist)):
            y = wherelist[i]
            if i + 1 == len(wherelist):
                x += y
            else:
                x += (y + ' and ')
        return x

    def runjob(self, id):
        global end_time
        table = dataExploration_RuleTable.objects.filter(id__in=id).values()
        # restableinfo = []
        # rescolumninfo = []
        for i in table:
            id = i['id']
            try:
                print(i)
                tableName = i['tableName']  # 表名
                pk = i['majorkey']  # 主键
                where = self.wherelistcond(eval(i['where']))
                columnsInfo = eval(i['columnsInfo'])  # 字段名
                columnsList = [i['column_name'] for i in columnsInfo]
                table = '[' + i['tableschema'] + '].' + '[' + tableName + ']'
                # if self.environment:
                #     table = self.source + '_dev' + '.' + tableName
                # else:
                #     table = self.source + '.' + tableName
                # print(table)
                start_time = datetime.datetime.now()  # 开始时间
                tableinfo, columninfo = self.Probejob.checkJob(table, where.replace(tableName, table), pk, columnsList,
                                                               columnsInfo, id)
                end_time = datetime.datetime.now()  # 结束时间
                delta = end_time - start_time
                delta_gmtime = time.gmtime(delta.total_seconds())
                duration_str = time.strftime("%H:%M:%S", delta_gmtime)
                tableinfo['runTime'] = duration_str
                tableinfo['status'] = 1
                tableinfo['statusdes'] = '成功'
                dataExploration_TableHistory.objects.create(**tableinfo)
                dataExploration_RuleTable.objects.filter(id=id).update(status=1, statusdes='成功')
            except Exception as f:
                # print(f)
                dataExploration_TableHistory.objects.create(tableId_id=id, status=4, statusdes='报错', comment=str(f),
                                                            probeTime=time.strftime('%Y-%m-%d %H:%M:%S'))
                dataExploration_RuleTable.objects.filter(id=id).update(status=4, statusdes='报错',
                                                                       LastProbeTime=time.strftime('%Y-%m-%d %H:%M:%S'))
            # restableinfo.append(tableinfo)
            # rescolumninfo = columninfo + rescolumninfo
        logger.info('探查结束')
        # dftableinfo = pd.DataFrame(restableinfo)
        # dfcolumninfo = pd.DataFrame(rescolumninfo)
        # # print(dftableinfo)
        # # print(dfcolumninfo)
        # writer = pd.ExcelWriter('dataTagExplorationres{end_time}.xlsx'.format(end_time=str(end_time)[0:10]))
        # dftableinfo.to_excel(writer, sheet_name='表信息', index=0)
        # dfcolumninfo.to_excel(writer, sheet_name='字段信息', index=0)
        # writer.save()
        # writer.close()
