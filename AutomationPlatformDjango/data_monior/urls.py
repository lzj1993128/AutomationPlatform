from django.conf.urls import url
from data_monior.views.datamonior.DataMoniorView import *

import logging

logger = logging.getLogger('log')

urlpatterns = [
    # 监控规则页面操作
    url('monior/MoniorHandle', monior_handle),
    # 获取监控规则数据
    url('monior/getmonior', get_monior),
    # 获取监控规则数据
    url('monior/gethistory', get_monior_history),
    # 获取图形数据
    url('monior/DayPassFail', day_pass_fail),
    # 获取规则分布
    url('monior/ruledistribution', rule_distribution),
    # 获取饼图分布
    url('monior/getpiecharts', get_pie_charts),
    # 保存处理信息
    url('monior/rulehandle', rule_handle),
    # 获取处理历史
    url('monior/getrulehandlehistory', get_rule_handle_history),
    # 获取表数据
    url('tablecheck/getdataworkstableinfo', get_dataworks_info),
    # 获取表字段信息
    url('tablecheck/getdataworkscolumninfo', get_dataworks_column_info),

    # 获取项目信息
    url('tablecheck/gettestproject', getTestProject),
    # 获取项目表信息
    url('tablecheck/getProTableInfo', getProTableInfo),
    # 提交项目表信息
    url('tablecheck/addProTableInfo', addProTableInfo),
    # 提交项目信息
    url('tablecheck/addProjectInfo', addProjectInfo),
    # 探查任务
    url('tablecheck/dataexplorationjob', dataexplorationjob),
    # 获取探查结果
    url('tablecheck/getexplorationres', getexplorationres),
    # 获取历史探查结果信息
    url('tablecheck/getexphistory', getexphistory),
    # 进一步探查结果
    url('tablecheck/datadetailsresult', datadetailsresult),
    # 字段进一步探查结果
    url('tablecheck/columnsdatadetails', columnsdatadetails),
    # sql解析
    url('tablecheck/analysisSql', analysisSql),
    # 保存测试用例
    url('tablecheck/addtestcase', addtestcase),
    # 获取测试用例
    url('tablecheck/gettestcase', gettestcase),
    # 执行测试用例
    url('tablecheck/runtestcase', runtestcase),
    # 执行测试用例执行记录
    url('tablecheck/getcasehistory', getcasehistory),

    # 获取问题列表增删改
    url('tablecheck/QuestionInfo', QuestionInfo),
    # 获取项目信息、人员信息 getprojectmodule
    url('tablecheck/getPrjUserinfo', getPrjUserinfo),
    # 获取项目模块 getprojectmodule
    url('tablecheck/getprojectmodule', getprojectmodule),
    # 获取问题列表 getquestionhistory getquestionhistoryrepeatSteps
    url('tablecheck/getquestioninfo', getquestioninfo),
    # 获取问题步骤信息
    url('tablecheck/getquestionrepeatSteps', getquestionrepeatSteps),
    # 获取问题处理历史
    url('tablecheck/getquestionhistory', getquestionhistory),
    # 保存问题处理历史
    url('tablecheck/QuestionHandleHistory', QuestionHandleHistory),
    # 发送钉钉提醒
    url('tablecheck/questionsenddingtalk', questionsenddingtalk),

    # 获取数据库信息
    url('tablecheck/getDatabase', getDatabase),
    # 任务实时日志
    url('tablecheck/nowtimelog', nowtimelog),
]
# from apscheduler.schedulers.background import BackgroundScheduler
# from data_monior.dataworksCrawler.Run_Job import run_job
#
#
# def twelve_time_job():
#     run_job().run_job_twelve_time()
#
#
# def eight_thirty_job():
#     run_job().run_job_eight_thirty_time()


# scheduler = BackgroundScheduler()
# scheduler.add_job(twelve_time_job, 'cron', day_of_week='*', hour=23, minute=59)
# scheduler.add_job(eight_thirty_job, 'cron', day_of_week='*', hour=8, minute=30)
# scheduler.start()
