#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/7/23 17:27
# @Author : LiZongJie
# @Site : 
# @File : sendDingtalk.py
# @Software: PyCharm
import os
import time
import requests
import pandas as pd
from utils.DbUtil import DatabaseUtil
from data_monior.dataworksTableCheck.servers.questionJob import questionJob
from data_monior.dataworksTableCheck.servers.DingTalkRobot import DingTalkRobot

dbUtil = DatabaseUtil()


class sendDingTalk(DingTalkRobot):
    def send_dataworks_alarm_rules(self, webhook):
        '''
        每天早上发送钉钉内容，dataworks报警规则汇总
        :return:
        '''
        sql = f'''
        select accountname 责任人,
                phone 责任人手机号,
                normal 正常,
                checkresult_1 橙色预警,
                checkresult_2 红色预警,
                checkresult_3 未运行规则,
                checkresult_error 规则报错,
                checkresult_no_handle 未处理,
                checkresult_handle 已处理
        from (
                SELECT
                        accountname ,
                        b.phone,
                        sum( CASE WHEN checkresult = 0 AND STATUS = 0 THEN 1 else 0 END ) normal,
                        sum( CASE WHEN checkresult = 1 AND STATUS = 0 THEN 1 else 0 END ) checkresult_1,
                        sum( CASE WHEN checkresult = 2 AND STATUS = 0 THEN 1 else 0 END ) checkresult_2,
                        sum( CASE WHEN checkresult = 3 AND STATUS = 0 THEN 1 else 0 END ) checkresult_3,
                        sum( CASE WHEN checkresult = - 2 AND STATUS = 0 THEN 1 else 0 END ) checkresult_error,
                        sum( CASE WHEN checkresult <> 0 AND STATUS = 0 AND handle_status = 0 THEN 1 else 0 END ) checkresult_no_handle,
                        sum( CASE WHEN checkresult <> 0 AND STATUS = 0 AND handle_status = 1 THEN 1 else 0 END ) checkresult_handle
                    FROM
                        data_monior_dataworks_alltables_rule_result a
                    left join api_user b on a.accountnameid=b.username
                    WHERE
                        job_run_date = '{self.send_date}'
                        AND table_schema in('nczbigdata','ncz_adm')
                    GROUP BY
                        accountname,b.phone ) a where checkresult_no_handle>0
                '''
        data = dbUtil.sql_to_dict(sql)
        df = pd.DataFrame(data)
        result = df.empty
        if result:
            pass
        else:
            at_mobiles = df['责任人手机号'].values.tolist()
            del df['责任人手机号']
            # result = df.empty
            # df_styled = df.style.background_gradient()
            self.generate_images(df)
            title = 'DataWorks监控'
            head = f'{self.send_date}个人监控汇总'
            top_message = '今日未处理的报警如下图，请相关人员在平台登记处理信息'
            follow_message = '请点击[监控平台](http://172.23.6.115:9527/#/)，登记处理情况'
            file = self.upload_image()  # 上传图片
            self.sendDingTalkMarkdown(webhook, title, head, top_message, file, follow_message, at_mobiles)
            os.remove(self.file_name)  # 删除下载的图片

    #
    def send_blink_dingrobot(self, webhook, file, at_mobiles, star, end):
        '''
        每天发送实时任务报错3次或者延时30分钟的任务
        :param webhook: 机器人
        :param file:
        :param at_mobiles:
        :param star:
        :param end:
        :return:
        '''
        title = 'Blink监控'
        head = '实时任务实例监控报警情况'
        top_message = f'报警时间范围：\n{star}-{end}'
        follow_message = ''
        self.sendDingTalkMarkdown(webhook, title, head, top_message, file, follow_message, at_mobiles)
        os.remove(self.file_name)

    def send_online_question(self):
        '''
        生成每日延期未处理的线上问题图片
        1.获取项目
        2.查看项目是否有需要跟踪的线上问题
        3.把线上问题发送钉钉群
        :return:
        '''

        def get_all_poject():
            sql = '''   select prj_id,prj_name,robot_group_id,md5(concat(prj_id, `create_time`)) file_name
                        from api_project where is_delete = 0 and robot_group_id<>'' 
                    '''
            data = dbUtil.sql_to_dict(sql)
            df = pd.DataFrame(data)
            return df.to_dict(orient='records')

        def get_robot_group_id(p_id):
            sql = f'''select p_id,web_hook,keywordList from config_robot where is_delete = 0 and p_id = {p_id}; '''
            data = dbUtil.sql_to_dict(sql)
            df = pd.DataFrame(data)
            return df['web_hook'].values.tolist()

        # 获取所有需要钉钉提醒的项目
        ProjectInfoList = get_all_poject()
        for ProjectInfo in ProjectInfoList:
            prj_id = ProjectInfo['prj_id']
            robot_group_id = ProjectInfo['robot_group_id']
            prj_name = ProjectInfo['prj_name']
            self.file_name = f"{ProjectInfo['file_name']}.png"
            # 查看项目是否有需要跟踪的线上问题
            data = questionJob().get_question_task_status(prj_id=prj_id)
            df = pd.DataFrame(data)
            if df.empty:
                pass
            else:
                df_warn = df[df['warnLogo'] == 1]
                df_warn_phone = df_warn.dropna(axis=0, subset=['currentAssignmentPhone'])
                result = df_warn.empty
                if result:
                    pass
                else:
                    web_hooklist = get_robot_group_id(robot_group_id)
                    df_res = df_warn[
                        ['prj_name', 'questionType', 'questionTitle', 'currentAssignmentTime', 'currentAssignment',
                         'planSolveTime',
                         'statusdes', 'taskstatus']]
                    df_res.columns = ['项目名字', '模块', '标题', '指派时间', '指派人', '计划解决时间', '解决状态', '计时']
                    at_mobiles = list(set(df_warn_phone['currentAssignmentPhone'].values.tolist()))
                    self.generate_images(df_res)
                    title = '线上问题'
                    head = '线上问题跟踪'
                    top_message = f'以下**【{prj_name}】**线上问题，请及时处理'
                    follow_message = '请点击[监控平台](http://172.23.6.115:9527/#/QuestionList)，登记处理情况'
                    file = self.upload_image()
                    for webhook in web_hooklist:
                        self.sendDingTalkMarkdown(webhook, title, head, top_message, file, follow_message, at_mobiles)
                    os.remove(self.file_name)

    def send_online_question_assign(self, webhook, project, at_mobiles, questiontitle, handler, currentAssignment,
                                    handleType,comment=None):
        '''

        :param webhook: 机器人
        :param project: 系统名称
        :param at_mobiles: 需要@的手机号
        :param questiontitle: 问题标题
        :param handler: 指派人
        :param currentAssignment: 被指派人
        :param handleType: 指派类型
        :return:
        '''
        title = '线上问题'
        head = '线上问题跟踪'
        if handleType == 2:
            top_message = f'问题已由**{currentAssignment}**解决，**{handler}**关闭'

        else:
            top_message = f'由**{handler}**指派给**{currentAssignment}**的问题'
            # print(comment)
            # if comment:
            #     message = f'**项目：**{project}\n\n**标题：**{questiontitle}\n\n**备注：**{comment}'
            # else:
            #     message = f'**项目：**{project}\n\n**标题：**{questiontitle}\n'
            # follow_message = '请点击[监控平台](http://172.23.6.115:9527/#/QuestionList)，登记处理情况'
        message = f'**项目：**{project}\n\n**标题：**{questiontitle}\n\n**备注：**{comment}'
        follow_message = '详情可点击[监控平台](http://172.23.6.115:9527/#/QuestionList)查看'
        self.sendDingTalkMarkdownNotImg(webhook, title, head, top_message, message, follow_message, at_mobiles)
        # sendDingTalkMarkdownNotImg

    def get_project_robot(self, prj_id):
        '''
        获取项目下的机器人
        :param prj_id:
        :return:
        '''
        sql = f'''
            SELECT
                prj_id,prj_name,group_name,robot_name,web_hook,keywordList
            FROM
                api_project a
                LEFT JOIN config_robot b ON a.robot_group_id = b.p_id 
            WHERE
                prj_id = {prj_id} and b.is_delete = 0
        '''
        data = dbUtil.sql_to_dict(sql)
        df = pd.DataFrame(data)
        if df.empty:
            robotlist = []
        else:
            robotlist = df['web_hook'].values.tolist()
        return robotlist

    def send_Error_Job(self, webhook, at_mobiles, job_name, run_time, res):
        title = '定时任务'
        head = '定时任务执行失败通知'
        top_message = f'**{job_name}**任务**{run_time}**执行失败'
        message = f'**失败原因：**{res}'
        follow_message = ''
        self.sendDingTalkMarkdownNotImg(webhook, title, head, top_message, message, follow_message, at_mobiles)
