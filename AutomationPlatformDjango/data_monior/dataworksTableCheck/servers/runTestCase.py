#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/19 10:41
# @Author : LiZongJie
# @Site : 
# @File : runRestCase.py
# @Software: PyCharm
from data_monior.dataworksTableCheck.servers.dataExploration import dataExploration
from data_monior.models import *
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import datetime
import time
import logging

logger = logging.getLogger('log')


class runtestcasejob(object):
    def __init__(self, user, password, project='nczbigdata'):
        '''
        初始化连接ODPS数据库,odps只能连接开发环境所有空间必须加dev
        :param project: 所属空间
        :param environment: 环境code
        :param environmentdes: 环境中文名
        '''
        logger.info('连接数据库')
        self.user = user
        self.password = password
        self.project = project  #
        self.odps = dataExploration(self.user, self.password, self.project + '_dev')
        logger.info('连接数据库成功')

    # def querysql(self, sql):
    #     result = self.odps.sqlquery(sql)
    #     return result

    def resultcheckvalve(self, resNum, expectValue, compareway):
        '''
        结果判断
        :param resNum: 实际值
        :param expectValue: 期望值
        :param compareway: 比较方式
        :return:
        '''
        if compareway == '=' and resNum == expectValue:
            res = 1
        elif compareway == '>' and resNum > expectValue:
            res = 1
        elif compareway == '<' and resNum < expectValue:
            res = 1
        elif compareway == '<=' and resNum <= expectValue:
            res = 1
        elif compareway == '>=' and resNum >= expectValue:
            res = 1
        elif compareway == '!=' and resNum != expectValue:
            res = 1
        else:
            res = 0
        return res

    # def clean(self, sql_str):
    #     # remove the /* */ comments
    #     q = re.sub(r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/", "", sql_str)
    #     print(q)
    #     # remove whole line -- and # comments
    #     lines = [line for line in q.splitlines() if not re.match("^\s*(--|#)", line)]
    #     print(lines)
    #     # remove trailing -- and # comments
    #     q = " ".join([re.split("--|#", line)[0] for line in lines])
    #     print(q)
    #     q = ' '.join(q.split())
    #     print(q)
    #     return q

    def runcase(self, caseinfo):
        sql = caseinfo['sql']
        start_time = datetime.datetime.now()  # 开始时间
        try:
            logger.info('【用例名称：{}】执行用例sql'.format(caseinfo['CaseName']))
            # sql查询结果
            results = self.odps.sqlquery(sql)
            logger.info('sql执行结束')
            logger.info('开始判断规则字段')
            # 用例字段规则信息
            columnrulelist = eval(caseinfo['columnRuleList'])
            df_results = pd.DataFrame(results)
            caseResult = []
            for columnrule in columnrulelist:
                expectValue = int(columnrule['expectValue'])  # 期望值
                compareway = columnrule['compareway']  # 比较方式
                # 判断数据是否符合期望值
                df_results['res'] = df_results[columnrule['columnName']].apply(
                    lambda x: self.resultcheckvalve(x, expectValue, compareway))
                # 如果存在一条数据不符合期望值，那么该用例失败
                reslist = df_results['res'].values.tolist()
                res = 2 if 0 in reslist else 1
                resdes = '失败' if res == 2 else '成功'
                if resdes == '失败':
                    caseres = df_results[df_results.res == 0]
                else:
                    caseres = df_results[df_results.res == 1]
                casereslist = caseres[columnrule['columnName']].values.tolist()
                result = casereslist[0]
                columnrule['status'] = res
                columnrule['statusdes'] = resdes
                columnrule['result'] = result
                caseResult.append(columnrule)
            df_columnrule = pd.DataFrame(columnrulelist)
            rescaselist = df_columnrule['status'].values.tolist()
            rescase = 2 if 2 in rescaselist else 1
            rescasedes = '失败' if rescase == 2 else '成功'
            end_time = datetime.datetime.now()  # 结束时间
            delta = end_time - start_time
            delta_gmtime = time.gmtime(delta.total_seconds())
            duration_str = time.strftime("%H:%M:%S", delta_gmtime)
            caseresult = {
                'caseId_id': caseinfo['id'], 'CaseName': caseinfo['CaseName'], 'caseResult': caseResult, 'sql': sql,
                'status': rescase, 'statusdes': rescasedes, 'starttime': start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'endtime': end_time.strftime("%Y-%m-%d %H:%M:%S"),
                'runtime': duration_str
            }
            print(caseresult)
            logger.info('判断结束，结果写入数据库')
            dataExploration_TestCase.objects.filter(id=caseinfo['id']).update(
                LastProbeTime=start_time.strftime("%Y-%m-%d %H:%M:%S"), status=rescase,
                statusdes=rescasedes)
            dataExploration_TestCaseRunHistory.objects.create(**caseresult)
            logger.info('【用例名称：{}】执行结束'.format(caseinfo['CaseName']))
            print('运行结束')
        except Exception as f:
            dataExploration_TestCase.objects.filter(id=caseinfo['id']).update(
                LastProbeTime=start_time.strftime("%Y-%m-%d %H:%M:%S"), status=4,
                statusdes='报错')
            dataExploration_TestCaseRunHistory.objects.create(caseId_id=caseinfo['id'], CaseName=caseinfo['CaseName'],
                                                              status=4, statusdes='报错', comment=str(f),caseResult=[])
        # print(df_results)
        # return results

    def runjob(self, id):
        caseinfolist = dataExploration_TestCase.objects.filter(id__in=id).values()
        max_workers = 5
        executor = ThreadPoolExecutor(max_workers=max_workers)  # 创建线程池
        all_task = [executor.submit(self.runcase, caseinfo) for caseinfo in caseinfolist]
        # for future in as_completed(all_task):
        #     data = future.result()
        #     print(data)
