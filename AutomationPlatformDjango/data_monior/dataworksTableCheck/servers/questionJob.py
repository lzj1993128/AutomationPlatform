#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/11/10 15:37
# @Author : LiZongJie
# @Site : 
# @File : questionJob.py
# @Software: PyCharm
import time, datetime
from utils.DbUtil import DatabaseUtil
# from data_monior.dataworksTableCheck.servers.DmsApi import DmsApi
from data_monior.models import *
import pandas as pd
from collections import defaultdict
import logging
from .DingTalkRobot import DingTalkRobot
import os

dbUtil = DatabaseUtil()
logger = logging.getLogger('log')


class questionJob(object):
    def get_question_task_status(self, prj_id, questionType=None):
        '''
        获取所有系统线上问题
        :return:
        '''
        sql = self.get_sql(prj_id, questionType)
        data = dbUtil.sql_to_dict(sql)
        for i in data:
            i['taskstatus'], i['warnLogo'] = self.time_diff(i['planSolveTime'], i['status'])
        return data

    def get_sql(self, prj_id, questionType):
        select = '''select id
                    ,questionID
                    ,prj_name
                    ,currentAssignmentID
                    ,currentAssignment
                    ,currentAssignmentPhone
                    ,currentAssignmentTime
                    ,planSolveTime
                    ,questionTitle
                    ,createDate
                    ,status
                    ,statusdes
                    ,is_delete
                    ,prj_id
                    ,questionChannels
                    ,questionType   '''
        tablefrom = ''' from data_monior_dataexploration_questioninfo '''
        where = ''' where  is_delete=0 '''
        order_by = ''' order by createDate desc '''
        if prj_id and questionType:
            whereand = f''' and prj_id={prj_id} and questionType='{questionType}' '''
        else:
            if prj_id != 0:
                whereand = f''' and prj_id={prj_id}'''
            else:
                whereand = ''
        sql = select + tablefrom + where + whereand + order_by
        # print(sql)
        return sql

    def time_diff(self, planSolveTime, status):
        '''
        1.判断任务是否延期 2.计算出对应延期时间 3.打上提醒标识
        不为已解决状态的任务 and (任务状态(task_status=1)and 时间小于10分钟(minutes < 10)) or (任务状态(task_status ==0))
        :param planSolveTime: 计划解决时间
        :param status: 任务状态 0 待解决 1解决中 2已解决
        :return:
        '''

        if planSolveTime:
            localTime = int(time.time())
            localTime = datetime.datetime.fromtimestamp(localTime)
            planSolveTimes = datetime.datetime.strptime(planSolveTime, "%Y-%m-%d %H:%M:%S")
            result = abs(localTime - planSolveTimes)
            hours = int(result.seconds / 3600)
            minutes = int(result.seconds % 3600 / 60)
            task_status = 1 if planSolveTimes >= localTime else 0
            task_statusdes = '剩余' if planSolveTimes >= localTime else '延期'
            warnLogo = 1 if status != 2 and (
                    (task_status == 1 and result.days == 0 and hours <= 5) or (task_status == 0)) else 0
            res = task_statusdes + str(result.days) + '天' + str(hours) + '小时' + str(
                minutes) + '分钟' if status != 2 else ''
        else:
            res = ''
            warnLogo = ''
        return res, warnLogo

    def get_Lead_warehouse_question(self, user, password, webhook):
        '''
        【前置仓可视化】本地已保存的问题和线上问题进行筛选后保存在本地数据库中
        :param user:
        :param password:
        :return:
        '''
        logger.info('开始获取前置仓dms数据库线上问题')
        dms_left = self.get_Lead_warehouse_dms_question(user, password)
        dms_left_column = dms_left.columns.tolist()
        local_right = self.get_Lead_warehouse_local_question()
        if local_right.empty:
            new_question_df = dms_left
            result_dict = dms_left.to_dict(orient='records')
            # self.save_Lead_warehouse_local_question(result_dict)
        else:
            new_df = pd.merge(dms_left, local_right, left_on='questionID', right_on='right_questionID', how='left',
                              suffixes=('', '_y'))
            res = new_df[new_df['right_questionID'].isnull()]
            new_question_df = res[dms_left_column]
            result_dict = new_question_df.to_dict(orient='records')
        self.save_Lead_warehouse_local_question(result_dict)
        if new_question_df.empty:
            logger.info('前置仓无新增线上问题')
        else:
            logger.info(f'前置仓新增线上问题：{len(new_question_df)}个')
            at_mobiles = list(set(new_question_df['currentAssignmentPhone'].values.tolist()))
            new_question_df = new_question_df[
                ['prj_name', 'questionType', 'questionTitle', 'handlerID', 'currentAssignmentTime', 'currentAssignment',
                 'planSolveTime',
                 'statusdes']]
            new_question_df.columns = ['项目名字', '问题模块', '问题标题', '创建人', '指派时间', '指派人', '计划解决时间', '解决状态']
            # print(new_question_df)
            # *******************************发送钉钉********************************
            title = '线上问题'
            head = '线上问题跟踪'
            top_message = f'前置仓新增线上问题：{len(new_question_df)}个'
            follow_message = '请点击[监控平台](http://172.23.6.115:9527/#/QuestionList)，登记处理情况'
            robot = DingTalkRobot(file_name='newquestion')
            robot.generate_images(new_question_df)
            file = robot.upload_image()
            robot.sendDingTalkMarkdown(webhook, title, head, top_message, file, follow_message, at_mobiles)
            os.remove(robot.file_name)
            # new_question_df =
            # sendDT = DingTalkRobot()
            # sendDT.generate_images(new_question_df)
            # file = sendDT.upload_image()

        # product_list_to_insert = [dataExploration_QuestionInfo(**i) for i in result_dict]
        # dataExploration_QuestionInfo.objects.bulk_create(product_list_to_insert)

    def save_Lead_warehouse_local_question(self, result_dict):
        '''
        【前置仓可视化】新增线上问题保存本地
        :param result_dict:
        :return:
        '''
        for i in result_dict:
            prj_id = i['prj_id']
            prj_name = i['prj_name']
            questionType = i['questionType']
            handlerID = i['handlerID']
            currentAssignmentID = i['currentAssignmentID']
            currentAssignmentPhone = i['currentAssignmentPhone']
            currentAssignment = i['currentAssignment']
            currentAssignmentTime = i['currentAssignmentTime']
            questionTitle = i['questionTitle']
            repeatSteps = i['repeatSteps']
            createDate = i['createDate']
            questionID = i['questionID']
            handleType = i['handleType']
            status = i['status']
            statusdes = i['statusdes']
            questionChannels = i['questionChannels']
            planSolveTime = i['planSolveTime']
            # dataExploration_QuestionInfo(prj_id=prj_id,prj_name)
            dataExploration_QuestionHandleHistory.objects.create(questionID=questionID, handleType=handleType,
                                                                 handlerID=handlerID, handler=handlerID,
                                                                 currentAssignmentID=currentAssignmentID,
                                                                 currentAssignment=currentAssignment,
                                                                 currentAssignmentPhone=currentAssignmentPhone,
                                                                 createDate=createDate)
            dataExploration_QuestionInfo.objects.create(prj_id=prj_id, prj_name=prj_name,
                                                        questionType=questionType,
                                                        currentAssignmentID=currentAssignmentID,
                                                        currentAssignmentPhone=currentAssignmentPhone,
                                                        currentAssignment=currentAssignment,
                                                        currentAssignmentTime=currentAssignmentTime,
                                                        questionTitle=questionTitle, repeatSteps=repeatSteps,
                                                        createDate=createDate, questionID=questionID,
                                                        status=status,
                                                        statusdes=statusdes, questionChannels=questionChannels,
                                                        planSolveTime=planSolveTime)

    def get_Lead_warehouse_local_question(self):
        '''
        【前置仓可视化】获取本地前置仓的所有线上问题
        :return:
        '''
        sql = '''SELECT questionID right_questionID FROM data_monior_dataexploration_questioninfo a 
                where  is_delete=0 and prj_id=1 order by id desc '''
        local_res = dbUtil.sql_to_dict(sql)
        local_df = pd.DataFrame(local_res)
        return local_df

    def get_Lead_warehouse_dms_question(self, user, password):
        '''
        【前置仓可视化】获取dms线上所有问题
        :param user:
        :param password:
        :return:
        '''
        request = DmsApi(user, password)
        dms_sql = '''
            SELECT  '1' as prj_id
                ,'前置仓可视化' as prj_name
                ,page_name AS questionType
                ,user_id as handlerID
                ,'333708' as currentAssignmentID
                ,'13175135839' as currentAssignmentPhone
                ,'张小权' as currentAssignment
                ,create_time as currentAssignmentTime
                ,contexts as questionTitle
                ,contexts as repeatSteps
                ,create_time as createDate
                ,md5(concat(id, `create_time`)) questionID
                ,0 handleType
                ,0 status
                ,'待解决' statusdes
                ,'APP端' questionChannels
                ,date_add(create_time,interval 1 day) planSolveTime
            FROM    visual_feedback_contexts 
            where `contexts` not like '%test%'
               and `contexts` not like '%Test%'
               and `contexts` not like '%测试%'
            '''
        res = request.sqlquery(dms_sql)
        dms_df = pd.DataFrame(res)
        return dms_df

    def get_project_tree(self):
        sql = '''
        SELECT
            a.all_code,
            CONCAT(a.all_name,'(',all_cnt,')') first_floor,
        -- 	a.all_name,
        -- 	all_cnt,
        -- 	a.prj_name,
            a.prj_id,
            CONCAT(a.prj_name,'(',prj_num,')') second_floor,
        -- 	prj_num,
            a.questionType,
            CONCAT(a.questionType,'(',cnt,')') three_floor,
            a.cnt 
        FROM
            (
            SELECT
                0 all_code,
                '全部' all_name,
                prj_name,
                prj_id,
                questionType,
                count( 1 ) cnt 
            FROM
                data_monior_dataexploration_questioninfo 
            WHERE
                is_delete = 0 
            GROUP BY
                prj_name,
                prj_id,
                questionType 
            ) a
            LEFT JOIN ( SELECT 0 all_code, '全部' all_num, count( 1 ) all_cnt FROM data_monior_dataexploration_questioninfo WHERE is_delete = 0 ) b ON a.all_code = b.all_code
            LEFT JOIN ( SELECT prj_name, prj_id, count( 1 ) prj_num FROM data_monior_dataexploration_questioninfo WHERE is_delete = 0 GROUP BY prj_name, prj_id ) c ON a.prj_id = c.prj_id
        '''
        res = dbUtil.sql_to_dict(sql)
        df = pd.DataFrame(res)
        first_floor = df[['all_code', 'first_floor']].drop_duplicates(subset=['all_code', 'first_floor'], keep='first')
        first_floor.columns = ['id', 'label']
        first_floor_dict = first_floor.to_dict(orient='record')
        d = defaultdict(lambda: defaultdict(list))
        for i in df.to_dict(orient='record'):
            d[i['prj_id']]['id'] = i['prj_id']
            d[i['prj_id']]['label'] = i['second_floor']
            d[i['prj_id']]['children'].append(
                {'id': i['prj_id'], 'questionType': i['questionType'], 'label': i['three_floor']})
        children = []
        for i in d.values():
            children.append(dict(i))
        first_floor_dict[0]['children'] = children
        # prjTreeData=res[0]['prjTreeData']
        # print(prjTreeData)
        return first_floor_dict
