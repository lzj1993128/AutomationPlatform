import json
import logging
import time
from datetime import datetime

from django.db.models import Q

from api.models import Plan, TaskHistory, Report
from api.service.plan.PlanService import PlanService
from api.service.report.ReportService import ReportService
from common.base.BaseService import BaseService
# from utils.CronUtil import CronUtil
from utils.EmailUtil import EmailUtil
from utils.PageUtil import PageUtil

logger = logging.getLogger('log')


class TaskService(BaseService):
    def __init__(self):
        self.pageUtil = PageUtil()
        self.planList = self.searchPlan()
        self.reportService = ReportService()
        self.emailUtil = EmailUtil()

    def searchPlan(self):
        """
        取出符合条件的计划运行
        :return:
        """
        planList = Plan.objects.filter(Q(is_delete='0') & Q(is_enable='True'))
        # 将query转化成list
        planList = self.pageUtil.searchSqlFieldData(planList)
        logger.info('执行的计划列表:{}'.format(planList))
        return planList

    def isInTime(self, sqlTimeStart, sqlTimeEnd):
        """
        获取当前时间，判断是否在时间内
        :param sqlTimeStart: 数据库存的时间段的开始
        :param sqlTimeEnd: 数据库存的时间段的结束
        :return:
        """
        timeNow = int(time.strftime("%H%M%S"))
        logger.info('打印出现在的时间{}'.format(timeNow))
        sqlTimeStart = int(sqlTimeStart.split(':')[0] + sqlTimeStart.split(':')[1] + '00')
        logger.info('打印数据库存在的开始时间,格式化成int:{}'.format(sqlTimeStart))
        sqlTimeEnd = int(sqlTimeEnd.split(':')[0] + sqlTimeEnd.split(':')[1] + '00')
        logger.info('打印数据库存在的结束时间,格式化成int:{}'.format(sqlTimeEnd))
        if sqlTimeStart <= timeNow <= sqlTimeEnd:
            logger.info('判断到该plan在设置的时间段内')
            return True
        else:
            logger.info('判断到该plan不在设置的时间段内')
            return False

    def isHaveRun(self, plan_id):
        """
        判断今天是否已经执行过
        :param plan_id:
        :return:布尔值
        """
        # 外键必须要先实例化
        plan = TaskHistory.objects.filter(plan_id=plan_id).order_by('-create_time')
        logger.info('plan:{}'.format(plan))
        if plan.count() != 0:
            logger.info('检测到有执行的结果,判断这个创建的年月日与当前时间年月日是否相等')
            # 如果计划存在，则判断创建时间
            plan = self.pageUtil.searchSqlFieldData(plan)[0]
            # 拆分最新一个计划执行的时间，和现在比较，如果都相等，则说明已经执行过
            create_time = plan.get('create_time')
            createTime = create_time.split(' ')[0]
            year = createTime.split('-')[0]
            mon = createTime.split('-')[1]
            day = createTime.split('-')[2]
            createTime = int(year + mon + day)
            logger.info('获取计划执行的时间,年月日转化成int:{}'.format(createTime))
            # 拆分现在的时间，年月日
            timeNow = int(time.strftime("%Y%m%d"))
            logger.info('获取当前的时间,年月日转化成int:{}'.format(createTime))
            if createTime == timeNow:
                logger.info('检测到今天已执行过该计划')
                return True
            else:
                logger.info('检测到今天未执行过该计划')
                return False
        else:
            logger.info('检测到今天未执行过该计划')
            return False

    def handleCron(self, cron):
        """
        处理cron表达式，如果下次执行之间和现在时间对比<10秒，则可以执行
        :param cron:
        :return:
        """
        nextTime = CronUtil().handleCron(cron, 1)[0]
        nextTime = datetime.strptime(nextTime, '%Y-%m-%d %H:%M:%S')
        logger.info('nextTime：{}'.format(nextTime))
        nowTime = datetime.now()
        logger.info('nowTime：{}'.format(nowTime))
        tdelta = nowTime - nextTime
        result = True if abs(tdelta.total_seconds()) < 15 else False
        return result

    def analyzePlan(self):
        """
        分析计划，用于执行
        :return:
        """
        if len(self.planList) == 0:
            logger.info('检测到没有可以执行的计划')
        else:
            for plan in self.planList:
                plan_id = int(plan.get('plan_id'))
                plan_name = plan.get('plan_name')
                envList = plan.get('envList')
                cron = plan.get('cron')
                # sqlTimeStart = plan.get('run_time_start')
                # sqlTimeEnd = plan.get('run_time_end')
                # 判断该计划今天是否已经执行过，判断该计划是否在执行的时间段内
                # isHaveRun = self.isHaveRun(plan_id)
                # isIntime = self.isInTime(sqlTimeStart, sqlTimeEnd)
                # 20211216新逻辑，cron表达式与现在时间差10秒，则可以执行
                result = self.handleCron(cron)
                if result:
                    logger.info('开始执行[{}]，将执行记录保存在TaskHistory'.format(plan_name))
                    planService = PlanService(plan_id, envList)
                    planService.runPlan()
                    logger.info('执行[{}]计划结束'.format(plan_name))
                    # 组合报告，发送邮件
                    title = plan_name + str(time.strftime("%Y%m%d"))
                    reportDataQuery = Report.objects.filter(plan_id=plan_id).order_by('-create_time')
                    reportDataList = self.pageUtil.searchSqlFieldData(reportDataQuery)[0]
                    report = self.reportService.handleReport(reportDataList)
                    # 查找计划中收件人的邮箱
                    emailList = json.loads(plan.get('emailList'))
                    if emailList:
                        logger.info('收件人不为空，发送邮件')
                        receiveEmailAddressList = self.getEmailAddressList(emailList)
                        self.emailUtil.sendEmail(report=report, to=receiveEmailAddressList, mail_title=title)
                else:
                    logger.info('该计划不符合执行条件,跳过')
                    continue

    def getEmailAddressList(self, emailList):
        """
        获取邮箱地址列表
        :param emailList:传入计划中的邮箱列表
        :return: 地址列表
        """
        emailAddressList = []
        try:
            if isinstance(emailList, list):
                for emailAddress in emailList:
                    address = emailAddress.get('email_address')
                    emailAddressList.append(address)
                logger.info('输出本次需要发送的邮箱{}'.format(emailAddressList))
        except Exception as e:
            logger.error('获取邮箱列表失败{}'.format(e))
        finally:
            return emailAddressList

    def runTask(self):
        """
        总的执行任务的入口
        :return:
        """
        try:
            self.analyzePlan()
        except Exception as e:
            logger.error('执行脚本异常信息{},不发送邮件'.format(e))
