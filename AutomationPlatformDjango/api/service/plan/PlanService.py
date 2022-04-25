import base64
import hashlib
import hmac
import json
import logging
import time
import urllib.parse
from datetime import datetime

from django.db.models import Q

from api.models import Plan, Case, Report, CaseTestResult,TaskHistory
from api.service.case.CaseService import CaseService
from api.service.mslog.MSLogService import MSLogService
from api.sqls.plan.PlanSql import countBigData
from big_data.models import BigData
from big_data.service.big_data.BigDataCompareService import BigDataComepareService
from common.base.BaseService import BaseService
from utils.DbUtil import DatabaseUtil
from utils.PageUtil import PageUtil

logger = logging.getLogger('log')
dbUtil = DatabaseUtil()


class PlanService(BaseService):
    def __init__(self, plan_id, envList=None, dbList=None):
        """
        初始化计划
        """
        self.plan_id = plan_id
        self.pageUtil = PageUtil()
        if envList is not None:
            self.envList = envList
        if dbList is not None:
            self.dbList = dbList
        self.report = self.addReport()
        self.bigDataList = json.loads(Plan.objects.get(plan_id=self.plan_id).bigDataList)

    def addReport(self):
        """
        生成测试报告，返回报告id
        :return:
        """
        now = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        plan_name = Plan.objects.get(plan_id=self.plan_id).plan_name
        # 报告名字为计划加当前时间
        report_name = plan_name + '_' + str(now)
        report = Report(plan_id=self.plan_id, report_name=report_name)
        report.save()
        report_id = report.report_id
        return report_id

    def getCase(self):
        """
        需要执行的用例
        新增：增加一个前置公共用例列表逻辑，确保执行单个计划时候只运行一次
        :return: 可以执行得用例
        """
        firstCaseRunList = []
        secondCaseRunList = []
        projectList = eval(Plan.objects.get(plan_id=self.plan_id).projectList)
        # 判断是保存的是项目还是用例
        if len(projectList) == 0:
            caseList = json.loads(Plan.objects.get(plan_id=self.plan_id).caseList)
            for case in caseList:
                case_id = case.get('case_id')
                firstCaseRunQuery = Case.objects.filter(Q(case_id=case_id) & Q(case_type='2') & Q(is_delete='0'))
                firstCaseRunList = firstCaseRunList + self.pageUtil.searchSqlFieldData(firstCaseRunQuery)
                secondCaseRunQuery = Case.objects.filter(
                    Q(case_id=case_id) & Q(case_type__in=['0', '1']) & Q(is_delete='0'))
                secondCaseRunList = secondCaseRunList + self.pageUtil.searchSqlFieldData(secondCaseRunQuery)
        else:
            for project in projectList:
                project_id = project.get('prj_id')
                firstCaseRunQuery = Case.objects.filter(Q(project_id=project_id), Q(case_type='2') & Q(is_delete='0'))
                firstCaseRunList = firstCaseRunList + self.pageUtil.searchSqlFieldData(firstCaseRunQuery)
                secondCaseRunQuery = Case.objects.filter(Q(project_id=project_id),
                                                         Q(case_type__in=['0', '1']) & Q(is_delete='0'))
                secondCaseRunList = secondCaseRunList + self.pageUtil.searchSqlFieldData(secondCaseRunQuery)
        totalRunCaseList = firstCaseRunList + secondCaseRunList
        return totalRunCaseList

    def analyzeCase(self):
        """
        增加公共前置用例只执行一次逻辑
        :param case_list: 用例列表
        :param flag: 区分公共前置用例还是普通用例
        :return:
        """
        case_list = self.getCase()
        for case in case_list:
            Plan.objects.filter(plan_id=self.plan_id).update(run_status=1)
            # 判断用例是否被删除，如果被删除，则不运行
            is_delete = case.get('is_delete')
            if is_delete == '1':
                continue
            case_type = case.get('case_type')
            step_info = json.loads(case.get('step_info'))
            # 判断用例是单接口用例，是一个接口对应多个多用例
            if int(case_type) == 0:
                logger.info('判断到用例是单接口用例')
                for stepCase in step_info:
                    needRunCase = []
                    stepDescription = stepCase.get('stepDescription')
                    needRunCase.append(stepCase)
                    self.runTestCase(case, needRunCase, stepDescription, case_type)
            else:
                self.runTestCase(case, step_info)
        # 更新计划的执行状态
        Plan.objects.filter(plan_id=self.plan_id).update(run_status=2)
        #  将执行的数据保存在Report表中
        self.statisticsCase()
        # 发送钉钉
        self.sendRobotList()

    def statisticsCase(self):
        """
        统计用例,写入报告
        :return:
        """
        pass_num = CaseTestResult.objects.filter(Q(report_id=self.report) & Q(result='Pass')).count()
        fail_num = CaseTestResult.objects.filter(Q(report_id=self.report) & Q(result='Fail')).count()
        error_num = CaseTestResult.objects.filter(Q(report_id=self.report) & Q(result='Error')).count()
        case_num = pass_num + fail_num + error_num
        Report.objects.filter(report_id=self.report).update(case_num=case_num, pass_num=pass_num, fail_num=fail_num,
                                                            error_num=error_num)

    def runTestCase(self, case, step_info, stepDescription=None, case_type=None):
        """
        运行case逻辑
        :param case:
        :param step_info:
        :param stepDescription:
        :return:
        """
        case_id = int(case.get('case_id'))
        case_name = case.get('case_name') + ':' + stepDescription
        report = Report.objects.get(report_id=self.report)
        caseService = CaseService(stepData=step_info, envData=self.envList, case_id=case_id, case_type=case_type)
        # 执行用例
        result = caseService.run_case()
        responseData = json.dumps(result)
        # 获取接口得执行结果
        isPass = result.get('isPass')
        mslog_name = mslog_path = None
        if isPass != 'Pass':
            logger.info('用例非通过状态，需要抓取微服务日志')
            msLogList = eval(Plan.objects.get(plan_id=self.plan_id).msLogList)
            if len(msLogList) > 0:
                logger.info('检测有日志配置列表，开始抓错误日志')
                mslogService = MSLogService(msLogList, self.report, case_id, case_name)
                mslogRseult = mslogService.runCatchMSLog()
                if mslogRseult:
                    logger.info('无配置的日志列表')
                    mslog_name = mslogRseult[0]
                    mslog_path = mslogRseult[1]
        # 数据驱动逻辑
        step_info = json.loads(case.get('step_info'))
        dataDrivenForm = self.get_target_value('dataDrivenForm', step_info, [])[0]
        nums = dataDrivenForm['nums']
        if case_type and int(nums) > 1:
            results = result.get('results')
            for i in results:
                assertResultList = i.get('assertResultList')
                caseTestResult = CaseTestResult(case_id=case_id, case_name=case_name, report=report, result=isPass,
                                                responseData=json.dumps(i), assertParamResult=assertResultList,
                                                mslog_name=mslog_name, mslog_path=mslog_path)
                caseTestResult.save()
        else:
            assertResultList = result.get('assertResultList')
            caseTestResult = CaseTestResult(case_id=case_id, case_name=case_name, report=report, result=isPass,
                                            responseData=responseData, assertParamResult=assertResultList,
                                            mslog_name=mslog_name, mslog_path=mslog_path)
            caseTestResult.save()
        logger.info('caseTestResult保存用例执行结果成功')

    def sendResultToCompanyWechat(self, webHookUrl, report_name, case_num, passPercent, pass_num, fail_num, error_num):
        """
        发送结果给企业微信
        :return:
        """
        content = '接口自动化报告名称:<font color=\"comment\"> **{}**</font> \n' \
                  '>总执行用例:<font color=\"comment\"> **{}**</font>\n' \
                  '>用例通过率:<font color=\"info\"> {} </font>\n' \
                  '>Pass用例:<font color=\"info\"> {}</font> \n' \
                  '>Fail用例:<font color=\"warning\"> {}</font> \n' \
                  '>Error用例:<font color=\"comment\"> {}</font> \n'.format(report_name, case_num, passPercent, pass_num,
                                                                          fail_num, error_num)
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        logger.info('发送企业微信自动化用例巡检')
        self.requestApi('post', webHookUrl, data=data, data_type='json')

    def sendRuseltToDingTalk(self, webHookUrl, secret, report_name, case_num, passPercent, pass_num, fail_num,
                             error_num, total_api_nums, pass_api_nums, fail_api_nums, error_api_nums, existPassPercent):
        """
        发送结果至钉钉
        :return:
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        if total_api_nums:
            content = "报告名称:**{}** \n\n" \
                      ">总比较用例: {} \n\n" \
                      ">比较通过率: {}  \n\n" \
                      ">比较Pass用例: {} \n\n" \
                      ">比较Fail用例: {} \n\n" \
                      ">比较Error用例: {} \n\n" \
                      ">总接口存在用例: {} \n\n" \
                      ">接口存在Pass用例: {} \n\n" \
                      ">接口存在Fail用例: {} \n\n" \
                      ">接口存在Error用例: {} \n\n" \
                      ">接口存在通过率: {} \n\n" \
                      "".format(report_name, case_num, passPercent, pass_num,
                                fail_num, error_num, total_api_nums, pass_api_nums, fail_api_nums,
                                error_api_nums, existPassPercent)
        else:
            content = "接口自动化测试报告名称:**{}** \n\n" \
                      ">总执行用例: {} \n\n" \
                      ">用例通过率: {}  \n\n" \
                      ">Pass用例: {} \n\n" \
                      ">Fail用例: {} \n\n" \
                      ">Error用例: {} \n\n" \
                      ">请点击[测试报告](http://172.23.6.115:9527/#/plan/PlanHome)进行查看".format(report_name, case_num,
                                                                                         passPercent, pass_num,
                                                                                         fail_num, error_num)

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "大数据测试",
                "text": content
            },
        }
        webHookUrl = '{}&timestamp={}&sign={}'.format(webHookUrl, timestamp, sign)
        logger.info('发送结果至钉钉群')
        self.requestApi('post', url=webHookUrl, data=data, data_type='json')

    def sendRobotList(self):
        """
        发送结果至机器人
        :return:
        """
        report_name = Report.objects.get(report_id=self.report).report_name
        case_num = Report.objects.get(Q(report_id=self.report)).case_num
        pass_num = Report.objects.get(Q(report_id=self.report)).pass_num
        fail_num = Report.objects.get(Q(report_id=self.report)).fail_num
        error_num = Report.objects.get(Q(report_id=self.report)).error_num
        # 接口存在数比较
        total_api_nums = Report.objects.get(Q(report_id=self.report)).api_total_nums
        pass_api_nums = Report.objects.get(Q(report_id=self.report)).pass_api_total_nums
        fail_api_nums = Report.objects.get(Q(report_id=self.report)).fail_api_total_nums
        error_api_nums = Report.objects.get(Q(report_id=self.report)).error_api_total_nums
        if int(case_num) != 0:
            passPercent = int(pass_num) / int(case_num)
            passPercent = 1 if passPercent > 1 else passPercent
            passPercent = '%.f%%' % (passPercent * 100)
        else:
            passPercent = '0%'
        # 计算字段占有
        existPassPercent = None
        if total_api_nums:
            if int(total_api_nums) != 0 and total_api_nums != None:
                existPassPercent = int(pass_api_nums) / int(total_api_nums)
                existPassPercent = '%.f%%' % (existPassPercent * 100)
            else:
                existPassPercent = '0%'
        rebotList = eval(Plan.objects.get(plan_id=self.plan_id).rebotList)
        if len(rebotList) != 0:
            for rebot in rebotList:
                webHookUrl = rebot.get('webHookUrl')
                if 'secret' in rebot.keys() and rebot.get('secret') != '':
                    secret = rebot.get('secret')
                    self.sendRuseltToDingTalk(webHookUrl, secret, report_name, case_num, passPercent, pass_num,
                                              fail_num, error_num, total_api_nums, pass_api_nums, fail_api_nums,
                                              error_api_nums, existPassPercent)
                else:
                    self.sendResultToCompanyWechat(webHookUrl, report_name, case_num, passPercent, pass_num, fail_num,
                                                   error_num)
        else:
            logger.info('没有添加群机器人，跳过执行')

    def runBigDataList(self):
        """
        获取大数据可执行用例,生成总的报告
        :return:
        """

        for bigData in self.bigDataList:
            big_data_id = bigData.get('big_data_id')
            if not BigData.objects.get(big_data_id=big_data_id).is_delete:
                # 如果大数据用例没有删除，先将大数据用例状态重置为0，再执行比较
                BigData.objects.filter(big_data_id=big_data_id).update(run_status='0')
                bigDataService = BigDataComepareService(big_data_id=big_data_id, envList=self.envList,
                                                        dbList=self.dbList, report_id=self.report)
                bigDataService.doRequestCompareFieldList()
            else:
                continue
        self.countBigDataReport()
        self.sendRobotList()

    def countBigDataReport(self):
        """
        统计大数据数据产生的结果，写入报告
        :return:
        """
        # 大数据比对通过数
        pass_num = dbUtil.sql_to_dict(countBigData('pass_compare_nums', self.report))[0].get('sum(pass_compare_nums)')
        # 大数据比对失败数
        fail_num = dbUtil.sql_to_dict(countBigData('fail_compare_nums', self.report))[0].get('sum(fail_compare_nums)')
        # 大数据比对错误数
        error_num = dbUtil.sql_to_dict(countBigData('error_compare_nums', self.report))[0].get(
            'sum(error_compare_nums)')
        # 大数据比对总数
        compare_num = dbUtil.sql_to_dict(countBigData('total_compare_nums', self.report))[0].get(
            'sum(total_compare_nums)')
        # 大数据字段存在通过数
        exist_pass_num = dbUtil.sql_to_dict(countBigData('pass_api_nums', self.report))[0].get('sum(pass_api_nums)')
        # 大数据字段存在失败数
        exist_fail_num = dbUtil.sql_to_dict(countBigData('fail_api_nums', self.report))[0].get('sum(fail_api_nums)')
        # 大数据存在错误数
        exist_error_num = dbUtil.sql_to_dict(countBigData('error_api_nums', self.report))[0].get('sum(error_api_nums)')
        # 大数据存在执行总数
        exist_total_num = dbUtil.sql_to_dict(countBigData('total_api_nums', self.report))[0].get('sum(total_api_nums)')
        # 将结果写入报告
        logger.info('将结果写入报告')
        Report.objects.filter(report_id=self.report).update(case_num=compare_num, pass_num=pass_num, fail_num=fail_num,
                                                            error_num=error_num, api_total_nums=exist_total_num,
                                                            pass_api_total_nums=exist_pass_num,
                                                            fail_api_total_nums=exist_fail_num,
                                                            error_api_total_nums=exist_error_num)

    def runPlan(self):
        """
        运行计划
        :return:
        """
        startTime = datetime.now()
        project_id = Plan.objects.get(plan_id=self.plan_id).project_id
        try:
            if len(self.bigDataList) != 0:
                self.runBigDataList()
            else:
                self.analyzeCase()
            endTime = datetime.now()
            runTime = (endTime - startTime).seconds
            task = TaskHistory(
                plan_id=self.plan_id, project_id=project_id, run_result='成功',
                start_time=startTime.strftime('%Y%m%d %H:%M:%S'), end_time=endTime.strftime('%Y%m%d %H:%M:%S'),
                run_time=runTime)
            task.save()
            logger.info('执行计划结束')
        except Exception as e:
            logger.info('执行计划异常{}'.format(e))
            endTime = datetime.now()
            runTime = (endTime - startTime).seconds
            task = TaskHistory(
                plan_id=self.plan_id, project_id=project_id, run_result='失败',
                start_time=startTime.strftime('%Y%m%d %H:%M:%S'), end_time=endTime.strftime('%Y%m%d %H:%M:%S'),
                run_time=runTime)
            task.save()
            msg = '执行计划异常'
            return msg
