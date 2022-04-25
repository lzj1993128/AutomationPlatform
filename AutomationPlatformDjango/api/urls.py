# -*- coding: utf-8 -*-

import logging

from django.conf.urls import url

from api.views.business.BussinessView import *
from api.views.case.CaseView import *
from api.views.database.DBView import *
from api.views.email.EmailView import *
from api.views.env.EnvView import *
from api.views.index.IndexView import *
from api.views.interface.InterfaceView import *
from api.views.job.JobView import *
from api.views.login.LoginView import *
from api.views.logsSocket.LogsSocketView import echo
from api.views.module.ModuleView import *
from api.views.mslog.MSLogView import *
from api.views.param.ParamView import *
from api.views.plan.PlanView import *
from api.views.project.ProjectView import *
from api.views.report.ReportView import *
from api.views.user.UserView import *
from api.views.robot.RobotView import *

logger = logging.getLogger('log')

urlpatterns = [
    # websocket
    url('echo', echo),

    # 登录模块
    url('login', login),
    url('user/info', userInfo),
    url('logout', logout),

    url('acLogin', acLogin),

    # 数据看板
    url('index/total', indexData),
    url('index/indexStatistics', indexStatistics),
    url('index/projectStatistics', totalData),

    # 接口页相关接口
    url('interface/getProjectInfo', getPrjectInfo),
    url('interface/add', interfaceAdd),
    url('interface/search', interfaceSearch),
    url('interface/delete', interfaceDelete),
    url('interface/upload', uploadImportExcel),
    url('interface/download', downloadImportExcel),
    url('interface/interfaceSearchById', interfaceSearchById),

    # 用例相关接口
    url('case/create/caseSearch', caseCreatCaseSearch),  # 用例创建页用例搜索
    url('case/create/moduleSearch', moduleSeach),  # 用例创建页模块获取
    url('case/create/runTestCase', caseRunTestCase),  # 测试用例运行
    url('case/create/addTestCase', addTestCase),  # 用例创建页新增用例
    url('case/list/deleteTestCase', deleteTestCase),  # 用例列表页删除
    url('case/create/editCase', editTestCase),  # 用例创建页编辑
    url('case/list/tree', getCaseTree),  # 获得用例管理页树

    # 项目相关接口
    url('project/add', projectAdd),
    url('project/search', projectSearch),
    url('project/update', projectUpdate),
    url('project/delete', projectDelete),

    # 模块相关接口
    url('module/add', moduleAdd),
    url('module/search', moduleSeach),
    url('module/delete', moduleDelete),

    # 计划相关接口
    url('plan/add', addPlan),
    url('plan/search', searchPlan),
    url('plan/runPlan', runPlan),
    url('plan/delete', deletePlan),
    url('plan/edit', editPlan),
    url('plan/cron', handleCronExp),
    url('plan/history', planRunHistory),

    # 报告相关接口
    url('report/search', searchReport),
    url('report/download', downLoadMSLog),

    # 性能脚本相关接口
    url('job/upload', uploadJobFile),  # 文件上传
    url('job/download', downloadJobFile),
    url('job/search', searchJobFile),
    url('job/delete', deleteJobFile),

    # 邮箱
    url('email/search', emailSearch),
    url('email/delete', emailDelete),
    url('email/sendEmail', emailSendEmail),
    url('email/add', emailAdd),

    # 环境
    url('env/add', envAdd),
    url('env/search', envSearch),
    url('env/delete', envDelete),

    # 微服务
    url('mslog/add', addMSLog),
    url('mslog/search', searchMSLog),
    url('mslog/delete', deleteMSLog),

    # 用户
    url('user/search', userSearch),
    url('user/add', userAdd),
    url('user/passwordUpdate', passwordUpdate),

    # 服务器
    url('db/add', addDB),
    url('db/delete', deleteDB),
    url('db/search', searchDB),

    # 业务域
    url('bd/add', businessAdd),
    url('bd/search', businessSearch),

    # 数据驱动
    url('param/add', paramAdd),
    url('param/search', paramSearch),

    # 机器人管理
    url('robot/add', addRebot),
    url('robot/search', searchRebot),
    url('robot/getById', getById),
    url('robot/robotDelete', robotDelete),
    url('robot/groupDelete', groupDelete),
    url('robot/getALLRebot', searchALLRebot)
]

from apscheduler.schedulers.background import BackgroundScheduler
from api.service.task.TaskService import TaskService

scheduler = BackgroundScheduler()


def job():
    logger.info('执行计划脚本,每15秒检测一次')
    taskHistory = TaskService()
    taskHistory.runTask()


sched = BackgroundScheduler(timezone='MST')
sched.add_job(job, 'interval', id='300_second_job', seconds=15)
# sched.start()
