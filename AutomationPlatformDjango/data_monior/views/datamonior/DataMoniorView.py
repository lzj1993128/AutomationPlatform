import json
import logging
import time

from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import threading
from Decorator.RequestDecorator import requestIntercept
from common.base.baseClass import getBodyData
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
from data_monior.data_monior.Data_Process import Data_Process
from data_monior.models import *
from api.models import *
# from django.db.models import Q
from utils.DbUtil import DatabaseUtil
from utils.PageUtil import PageUtil
from data_monior.dataworksTableCheck.servers.sendDingtalk import sendDingTalk
from data_monior.dataworksTableCheck.servers.dataExploration import dataExploration
from data_monior.dataworksTableCheck.servers.dataCheck import datacheck
from data_monior.dataworksTableCheck.servers.columnsdetails import detailscheck
# from data_monior.dataworksTableCheck.servers.analysisSql import sqlParse
from data_monior.dataworksTableCheck.servers.runTestCase import runtestcasejob
from data_monior.dataworksTableCheck.servers.questionJob import questionJob

logger = logging.getLogger('log')
date = time.strftime('%Y%m%d %H:%M:%S')
success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()
questionJobs = questionJob()
user = 'LTAI4GHKZBiC7EPpCjuN1kNU'
password = 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL'


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def monior_handle(request):
    """
    监控规则，
    字段opt_type，判断操作
    编辑：edit
    删除：delete
    启用：enable
    添加：add
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        project = requestData.get('project')
        table = requestData.get('table')
        rule_sql = requestData.get('rule_sql')
        check_way = requestData.get('check_way')
        check_type = requestData.get('check_type')
        desired_value = requestData.get('desired_value')
        compare_way = requestData.get('compare_way')
        rule_name = requestData.get('rule_name')
        describe = requestData.get('describe')
        person = requestData.get('person')
        person_phone = requestData.get('person_phone')
        opt_type = requestData.get('opt_type')
        if opt_type == 'add':
            big_data = Datamonior(project=project,
                                  table=table,
                                  rule_sql=rule_sql,
                                  check_way=check_way,
                                  check_type=check_type,
                                  desired_value=desired_value,
                                  compare_way=compare_way,
                                  rule_name=rule_name,
                                  describe=describe,
                                  person=person,
                                  person_phone=person_phone,
                                  creat_time=date,
                                  update_time=date
                                  )
            big_data.save()
            responseData = success.success_response()
            responseData['message'] = '保存成功'
        if opt_type == 'edit':
            get_id = requestData.get('id')
            Datamonior.objects.filter(id=get_id).update(project=project,
                                                        table=table,
                                                        rule_sql=rule_sql,
                                                        check_way=check_way,
                                                        check_type=check_type,
                                                        desired_value=desired_value,
                                                        compare_way=compare_way,
                                                        rule_name=rule_name,
                                                        describe=describe,
                                                        person=person,
                                                        person_phone=person_phone,
                                                        update_time=date
                                                        )
            responseData = success.success_response()
            responseData['message'] = '修改成功'
        if opt_type == 'enable':
            # 启用/删除
            get_id = requestData.get('id')
            is_enable = requestData.get('is_enable')
            Datamonior.objects.filter(id=get_id).update(is_enable=is_enable)
            responseData = success.success_response()
            responseData['message'] = '成功'
        if opt_type == 'delete':
            get_id = requestData.get('id')
            is_delete = requestData.get('is_delete')
            Datamonior.objects.filter(id=get_id).update(is_delete=is_delete)
            responseData = success.success_response()
            responseData['message'] = '删除成功'
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def get_monior(request):
    """
    获取规则信息
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        rule_name = requestData.get('rule_name')
        if rule_name != '':
            table = Datamonior.objects.filter(rule_name__contains=rule_name)
        else:
            table = Datamonior.objects.all()
        _data = pageUtil.searchSqlFieldData(table)
        responseData = success.success_response()
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
# @requestIntercept
def get_monior_history(request):
    """
    获取任务执行数据
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        run_date = requestData.get('run_date')
        rule_id = requestData.get('rule_id')
        status = requestData.get('status')
        table_schema = requestData.get('table_schema')
        accountname = requestData.get('accountname')
        handle_status = requestData.get('handle_status')
        callback = None
    else:
        page = int(request.GET.get('page'))
        pageSize = int(request.GET.get('pageSize'))
        run_date = request.GET.get('run_date')
        rule_id = request.GET.get('rule_id')
        status = request.GET.get('status')
        table_schema = request.GET.get('table_schema')
        accountname = request.GET.get('accountname')
        handle_status = request.GET.get('handle_status')
        callback = request.GET.get('callback')
    search_dict = dict()
    if rule_id:
        search_dict['ruleid'] = rule_id
    if run_date:
        search_dict['job_run_date'] = run_date
    if status:
        search_dict['checkresult'] = int(status)
    if table_schema:
        search_dict['table_schema'] = table_schema
    if accountname:
        search_dict['accountname'] = accountname
    if handle_status:
        search_dict['handle_status'] = handle_status
    table = dataworks_alltables_rule_result.objects.filter(**search_dict).order_by("-job_run_date")
    _data = pageUtil.searchSqlFieldData(table)
    responseData = success.success_response()
    pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
    _data = pageUtil.getDataInfo(_data, page, pageSize)
    responseData['data'] = _data
    responseData['pageInfo'] = pageInfo
    if callback:
        callback = request.GET.get('callback')
        responseData = callback + '(' + json.dumps(responseData) + ')'
        return HttpResponse(responseData)
    else:
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
# @requestIntercept
def day_pass_fail(request):
    """
    获取图形数据
    :param request:
    """
    if request.method == 'GET':
        type = request.GET.get('type')
        if type == 'LineChart':
            sql = Data_Process().data_sql()
            result_ = dbUtil.sql_to_dict(sql)
            result = Data_Process().data_linechart(result_)
        elif type == 'SingleRuleRunHistory':
            rule_id = request.GET.get('rule_id')
            sql = Data_Process().data_sql2(rule_id)
            result_ = dbUtil.sql_to_dict(sql)
            # conduct_history = dataworks_rule_handle.objects.filter(ruleid=rule_id).order_by("-conduct_time")
            # conduct_historys_list = pageUtil.searchSqlFieldData(conduct_history)
            result = Data_Process().data_SingleRuleRunHistory(result_)
            # result['conduct_historys_list'] = conduct_historys_list
            # print(result)
        responseData = success.success_response()
        responseData['result'] = result
        if 'callback' in request.GET.keys():
            callback = request.GET.get('callback')
            responseData = callback + '(' + json.dumps(responseData) + ')'
            return HttpResponse(responseData)
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
# @requestIntercept

def rule_distribution(request):
    """
    获取规则分布数据
    :param request:
    """
    if request.method == 'GET':
        table_schema = request.GET.get('table_schema')
        run_date = time.strftime('%Y-%m-%d')
        sql = Data_Process().data_sql4(run_date, table_schema)
        _data = dbUtil.sql_to_dict(sql)
        result = Data_Process().dataworks_category(_data)
        responseData = success.success_response()
        responseData['result'] = result
        if 'callback' in request.GET.keys():
            callback = request.GET.get('callback')
            responseData = callback + '(' + json.dumps(responseData) + ')'
            return HttpResponse(responseData)
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
# @requestIntercept
def get_pie_charts(request):
    """
    获取饼图数据
    :param request:
    """
    if request.method == 'GET':
        pro_dict = {'nczbigdata': '数仓', 'ncz_adm': '数仓-档案集', 'nczalgo': '算法'}
        sql = Data_Process().data_sql3()
        result_ = dbUtil.sql_to_dict(sql)
        result = Data_Process().data_piechart(result_, pro_dict)
        responseData = success.success_response()
        responseData['result'] = result
        if 'callback' in request.GET.keys():
            callback = request.GET.get('callback')
            responseData = callback + '(' + json.dumps(responseData) + ')'
            return HttpResponse(responseData)
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def rule_handle(request):
    if request.method == 'POST':
        # resondict = {1: '代码逻辑问题', 2: '监控规则问题', 3: '业务系统问题', 4: '其他', 5: '误报'}
        requestData = getBodyData(request.body)
        conduct_id = requestData.get('id')
        ruleid = requestData.get('ruleid')
        reson = requestData.get('reson')
        conduct = requestData.get('conduct')
        person = requestData.get('person')
        over_time = requestData.get('over_time')
        job_run_date = requestData.get('job_run_date')
        resontype = requestData.get('resontype')
        resontypedes = requestData.get('resontypedes')
        big_data = dataworks_rule_handle(
            ruleid=ruleid, reson=reson, conduct=conduct, over_time=over_time,
            conduct_time=time.strftime('%Y-%m-%d %H:%M:%S'), person=person, conduct_id=conduct_id,
            resontypedes=resontypedes, resontype=resontype
        )
        big_data.save()
        dataworks_alltables_rule_result.objects.filter(job_run_date=job_run_date, ruleid=ruleid).update(
            handle_status=1, over_time=over_time, resontypedes=resontypedes, resontype=resontype
        )
        responseData = success.success_response()
        responseData['message'] = '处理成功'
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def get_rule_handle_history(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        rule_id = requestData.get('rule_id')
        conduct_history = dataworks_rule_handle.objects.filter(ruleid=rule_id).order_by("-conduct_time")
        _data = pageUtil.searchSqlFieldData(conduct_history)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def get_dataworks_info(request):
    if request.method == 'GET':
        source = request.GET.get('source')
        db_info = Database.objects.filter(db_id=source).values()
        # user = 'LTAI4GHKZBiC7EPpCjuN1kNU'
        # password = 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL'
        odps = dataExploration(list(db_info)[0])
        result = odps.gettableinfo(table=None)
        responseData = success.success_response()
        responseData['result'] = result
        # responseData['resultlist'] = resultlist
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def get_dataworks_column_info(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        source = requestData.get('source')
        old_table = requestData.get('table')
        # user = 'LTAI4GHKZBiC7EPpCjuN1kNU'
        # password = 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL'
        db_info = Database.objects.filter(db_id=source).values()
        odps = dataExploration(list(db_info)[0])
        columnsinfo, columnsList = odps.gettablecolumnsinfo(old_table)
        responseData = success.success_response()
        responseData['columnsinfo'] = columnsinfo
        responseData['columnsList'] = columnsList
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getTestProject(request):
    """
    获取项目信息
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        table = dataExploration_Project.objects.all()
        _data = pageUtil.searchSqlFieldData(table)
        responseData = success.success_response()
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getProTableInfo(request):
    """
    获取表信息
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        proId_id = requestData.get('proId_id')
        table = dataExploration_RuleTable.objects.filter(proId_id=proId_id, is_delete=0).values()
        # _data = pageUtil.searchSqlFieldData(table)
        data = []
        for i in table:
            i['majorkey'] = eval(i['majorkey'])
            i['where'] = eval(i['where'])
            i['columnsInfo'] = eval(i['columnsInfo'])
            data.append(i)
        responseData = success.success_response()
        pageInfo = pageUtil.getPageInfo(data, page, pageSize)
        data = pageUtil.getDataInfo(data, page, pageSize)
        responseData['data'] = data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def addProTableInfo(request):
    """
    项目表信息增删改
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        type = requestData['type']
        if type == 'add':
            tableinfo = requestData['tableinfo']
            proId_id = tableinfo['proId_id']
            # environment = tableinfo['environment']
            # environmentdes = tableinfo['environmentdes']
            tableName = tableinfo['tableName']
            tableChName = tableinfo['tableChName']
            source = tableinfo['source']
            majorkey = tableinfo['majorkey']
            columnsInfo = tableinfo['columnList']
            createPersons = tableinfo['createPersons']
            where = tableinfo['wherelist']
            big_data = dataExploration_RuleTable(proId_id=proId_id,
                                                 tableName=tableName, tableChName=tableChName, source=source,
                                                 majorkey=majorkey, columnsInfo=columnsInfo,
                                                 createPersons=createPersons,
                                                 where=where)
            big_data.save()
            responseData = success.success_response()
            responseData['message'] = '新增成功'
        if type == 'del':
            get_id = requestData.get('id')
            is_delete = requestData.get('is_delete')
            dataExploration_RuleTable.objects.filter(id=get_id).update(is_delete=is_delete)
            responseData = success.success_response()
            responseData['message'] = '删除成功'
        if type == 'edit':
            # get_id = requestData.get('id')
            tableinfo = requestData['tableinfo']
            get_id = tableinfo['id']
            proId_id = tableinfo['proId_id']
            tableName = tableinfo['tableName']
            tableChName = tableinfo['tableChName']
            source = tableinfo['source']
            majorkey = tableinfo['majorkey']
            columnsInfo = tableinfo['columnList']
            createPersons = tableinfo['createPersons']
            where = tableinfo['wherelist']
            dataExploration_RuleTable.objects.filter(id=get_id).update(proId_id=proId_id,
                                                                       tableName=tableName, tableChName=tableChName,
                                                                       source=source,
                                                                       majorkey=majorkey, columnsInfo=columnsInfo,
                                                                       createPersons=createPersons,
                                                                       where=where
                                                                       )
            responseData = success.success_response()
            responseData['message'] = '修改成功'
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def addProjectInfo(request):
    """
    项目信息增删改
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        type = requestData.get('type')
        Project = requestData.get('Project')
        Project_id = requestData.get('Project_id')
        IterationName = requestData.get('IterationName')
        State = requestData.get('State')
        Statedes = requestData.get('Statedes')
        DevPersons = requestData.get('DevPersons')
        TestPersons = requestData.get('TestPersons')
        ScheduleTestTime = requestData.get('ScheduleTestTime')
        PlannedReleaseDate = requestData.get('PlannedReleaseDate')

        responseData = success.success_response()
        if type == 'add':
            big_data = dataExploration_Project(Project=Project, IterationName=IterationName, State=State,
                                               DevPersons=DevPersons, TestPersons=TestPersons,
                                               ScheduleTestTime=ScheduleTestTime,
                                               PlannedReleaseDate=PlannedReleaseDate, Statedes=Statedes,
                                               Project_id=Project_id)
            big_data.save()
            # dataExploration_Project.objects.create(**requestData)
            responseData['message'] = '新增成功'
        if type == 'del':
            get_id = requestData.get('id')
            is_delete = requestData.get('is_delete')
            dataExploration_Project.objects.filter(id=get_id).update(is_delete=is_delete)

            responseData['message'] = '删除成功'
        if type == 'edit':
            get_id = requestData.get('id')
            dataExploration_Project.objects.filter(id=get_id).update(Project=Project, IterationName=IterationName,
                                                                     State=State,
                                                                     DevPersons=DevPersons, TestPersons=TestPersons,
                                                                     ScheduleTestTime=ScheduleTestTime,
                                                                     PlannedReleaseDate=PlannedReleaseDate,
                                                                     Statedes=Statedes
                                                                     )

            responseData['message'] = '修改成功'
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def dataexplorationjob(request):
    """
    数据探查
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        print(requestData)
        id = requestData.get('id')
        environment = requestData.get('environment')  # 环境code:0线上 1开发
        environmentdes = requestData.get('environmentdes')  # 环境
        source = requestData.get('source')  # 数据源
        db_info = Database.objects.filter(db_id=source).values()
        # odps = dataExploration(list(db_info)[0])
        dataExploration_RuleTable.objects.filter(id__in=id).update(status=3, statusdes='探查中')
        job = datacheck(list(db_info)[0], environment, environmentdes)
        thread = threading.Thread(target=job.runjob, args=([id]))
        thread.start()
        responseData = success.success_response()
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getexplorationres(request):
    """
    获取探查结果
    :param request:
    """
    if request.method == 'GET':
        tableid = request.GET.get('tableid')
        id = request.GET.get('id')
        if tableid:
            tableinfo = dataExploration_TableHistory.objects.filter(tableId_id=tableid).values().last()
        if id:
            tableinfo = dataExploration_TableHistory.objects.filter(id=id).values()[0]
        try:
            tableinfo['majorkey'] = eval(tableinfo['majorkey'])
            tableinfo['where'] = eval(tableinfo['where'])
            taskId = tableinfo['taskId']
            tableColumnList = dataExploration_TableColumnsHistory.objects.filter(taskId=taskId).all()
            tableColumnList = pageUtil.searchSqlFieldData(tableColumnList)
            TableDynamicheader = dataExploration_TableDynamicheader.objects.all()
            TableDynamicheader = pageUtil.searchSqlFieldData(TableDynamicheader)
        except:
            tableinfo = []
            tableColumnList = []
            TableDynamicheader = []
        # print(tableColumnList)
        responseData = success.success_response()
        responseData['tableinfo'] = tableinfo
        responseData['tableColumnList'] = tableColumnList
        responseData['TableDynamicheader'] = TableDynamicheader
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getexphistory(request):
    """
    获取历史探查结果
    :param request:
    """
    if request.method == 'GET':
        tableid = request.GET.get('tableid')
        tableinfo = dataExploration_TableHistory.objects.filter(tableId_id=tableid).values().order_by("-probeTime")
        print(tableinfo)
        # _data = pageUtil.searchSqlFieldData(tableinfo)
        responseData = success.success_response()
        responseData['data'] = list(tableinfo)
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def datadetailsresult(request):
    """
    获取重复数据探查结果
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        sql = requestData.get('sql')
        source = requestData.get('source')  # 数据源
        odps = dataExploration(user, password, source + '_dev')
        result = odps.sqlquery(sql)
        try:
            columnlist = list(result[0].keys())
        except:
            columnlist = []
        responseData = success.success_response()
        responseData['result'] = result
        responseData['columnlist'] = columnlist
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def columnsdatadetails(request):
    """
    获取字段进一步探查结果
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        details = detailscheck(requestData, user, password)
        result, sql = details.detailsdata()
        try:
            columnlist = list(result[0].keys())
        except:
            columnlist = []
        responseData = success.success_response()
        responseData['result'] = result
        responseData['columnlist'] = columnlist
        responseData['sql'] = sql
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def analysisSql(request):
    """
    sql解析
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        try:
            sql = requestData.get('sql')
            columnList = sqlParse().get_query_columns(sql)
            result = 'sql解析成功'
            code = 200
        except Exception as f:
            columnList = []
            result = str(f)
            code = 201
        responseData = success.success_response()
        responseData['columnList'] = columnList
        responseData['message'] = result
        responseData['code'] = code
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def addtestcase(request):
    """
    测试用例
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        responseData = success.success_response()
        if requestData['opt_type'] == 'add':
            caseinfo = requestData['caseinfo']
            dataExploration_TestCase.objects.create(**caseinfo)
            responseData['message'] = '保存成功'
        elif requestData['opt_type'] == 'delete':
            get_id = requestData.get('id')
            is_delete = requestData.get('is_delete')
            dataExploration_TestCase.objects.filter(id=get_id).update(is_delete=is_delete)
            responseData['message'] = '删除成功'
        elif requestData['opt_type'] == 'edit':
            caseinfo = requestData['caseinfo']
            dataExploration_TestCase.objects.filter(id=caseinfo['id']).update(**caseinfo)
            responseData['message'] = '修改成功'
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def gettestcase(request):
    """
    获取测试用例
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        proId_id = requestData.get('proId_id')
        CaseName = requestData.get('CaseName')
        if CaseName != '':
            caselist = Datamonior.objects.filter(CaseName__contains=CaseName, proId_id=proId_id, is_delete=0)
        else:
            caselist = dataExploration_TestCase.objects.filter(proId_id=proId_id, is_delete=0).values()
        # _data = pageUtil.searchSqlFieldData(caselist)
        responseData = success.success_response()
        if len(caselist) != 0:
            data = []
            for i in caselist:
                # i['column'] = eval(i['column'])
                i['columnRuleList'] = eval(i['columnRuleList'])
                data.append(i)
            pageInfo = pageUtil.getPageInfo(caselist, page, pageSize)
            data = pageUtil.getDataInfo(caselist, page, pageSize)
            responseData['data'] = data
            responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def runtestcase(request):
    """
    执行测试用例
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        id = requestData.get('id')
        dataExploration_TestCase.objects.filter(id__in=id).update(status=3, statusdes='运行中')
        job = runtestcasejob(user, password)
        thread = threading.Thread(target=job.runjob, args=([id]))
        thread.start()
        responseData = success.success_response()
        responseData['message'] = '运行中'
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getcasehistory(request):
    """
    获取测试用例执行记录
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        caseId_id = requestData.get('id')
        casehistorylist = dataExploration_TestCaseRunHistory.objects.filter(caseId_id=caseId_id).values().order_by(
            "-starttime")
        # _data = pageUtil.searchSqlFieldData(casehistorylist)
        data = []
        for i in casehistorylist:
            i['caseResult'] = eval(i['caseResult'])
            data.append(i)
        responseData = success.success_response()
        responseData['data'] = data
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def QuestionInfo(request):
    """
    线上问题信息
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        responseData = success.success_response()
        if requestData['type'] == 'add':
            import hashlib
            def create_id():
                m = hashlib.md5(str(datetime.datetime.now()).encode('utf-8'))
                return m.hexdigest()

            handlerID = requestData['handlerID']  # 指派人工号
            handleType = requestData['handleType']  # 类型
            handler = requestData['handler']  # 指派人名字
            questionID = create_id()
            questioninfo = requestData['questioninfo']
            questioninfo['questionID'] = questionID
            createDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            questioninfo['createDate'] = createDate
            questioninfo['currentAssignmentTime'] = createDate
            questioninfohistory = {'questionID': questionID, 'handleType': handleType, 'handlerID': handlerID,
                                   'handler': handler,
                                   'currentAssignmentID': questioninfo['currentAssignmentID'],
                                   'currentAssignment': questioninfo['currentAssignment'],
                                   'currentAssignmentPhone': questioninfo['currentAssignmentPhone'],
                                   'createDate': createDate}
            dataExploration_QuestionInfo.objects.create(**questioninfo)
            dataExploration_QuestionHandleHistory.objects.create(**questioninfohistory)
            responseData['message'] = '保存成功'
        elif requestData['type'] == 'del':
            get_id = requestData.get('id')
            dataExploration_QuestionInfo.objects.filter(id=get_id).update(is_delete=1)
            responseData['message'] = '删除成功'
        elif requestData['type'] == 'edit':
            questioninfo = requestData['questioninfo']
            del questioninfo['taskstatus']
            del questioninfo['warnLogo']
            dataExploration_QuestionInfo.objects.filter(id=questioninfo['id']).update(**questioninfo)
            responseData['message'] = '修改成功'
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def QuestionHandleHistory(request):
    """
    线上问题信息
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        responseData = success.success_response()
        handleType = requestData['handleType']  # 类型
        questionID = requestData['questionID']
        currentAssignmentID = requestData['currentAssignmentID']
        currentAssignment = requestData['currentAssignment']
        currentAssignmentPhone = requestData['currentAssignmentPhone']
        currentAssignmentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        requestData['createDate'] = currentAssignmentTime
        if handleType == 1:
            status = 1
            statusdes = '解决中'
            res = {'currentAssignmentID': currentAssignmentID, 'currentAssignment': currentAssignment,
                   'currentAssignmentPhone': currentAssignmentPhone, 'currentAssignmentTime': currentAssignmentTime,
                   'status': status, 'statusdes': statusdes}
            dataExploration_QuestionHandleHistory.objects.create(**requestData)
            dataExploration_QuestionInfo.objects.filter(questionID=questionID).update(**res)
            responseData['message'] = '指派成功'
        elif handleType == 2:
            status = 2
            statusdes = '已解决'
            res = {'currentAssignmentID': currentAssignmentID, 'currentAssignment': currentAssignment,
                   'currentAssignmentPhone': currentAssignmentPhone, 'currentAssignmentTime': currentAssignmentTime,
                   'status': status, 'statusdes': statusdes, 'Type': requestData['Type']}
            dataExploration_QuestionHandleHistory.objects.create(**requestData)
            dataExploration_QuestionInfo.objects.filter(questionID=questionID).update(**res)
            responseData['message'] = '关闭成功'
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getPrjUserinfo(request):
    """
    获取项目信息、人员信息、侧边树
    :param request:
    """
    if request.method == 'GET':
        from django.db.models import Count
        # requestData = getBodyData(request.body)

        prj = Project.objects.filter(is_delete=0).values().order_by("-create_time")
        # userobj = User.objects.filter(is_active=1).values('user_id', 'username', 'nickname', 'phone')
        # sidetree = dataExploration_QuestionInfo.objects.filter(is_delete=0).values("prj_name", "prj_id").annotate(
        #     c=Count('id'))
        # allnum = dataExploration_QuestionInfo.objects.filter(is_delete=0).aggregate(c=Count('id'))
        # sidetreelist = [{'id': i['prj_id'], 'label': i['prj_name'] + '(' + str(i['c']) + ')'} for i in list(sidetree)]
        # prjTreeData = questionJobs.get_project_tree()
        responseData = success.success_response()
        responseData['prjlist'] = list(prj)
        # responseData['userlist'] = list(userobj)
        # responseData['prjTreeData'] = prjTreeData
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getDatabase(request):
    """
    获取数据库信息
    :param request:
    """
    if request.method == 'GET':
        database_List = Database.objects.filter(is_delete=0).values()
        responseData = success.success_response()
        responseData['data'] = list(database_List)
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getquestioninfo(request):
    """
    获取问题信息
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        prj_id = requestData.get('chooseid')
        questionType = requestData.get('choosename')
        # print(prj_id,questionType)
        # accesskey = '94e4dca163499d8e760440493e040dd9b7c6bb4d88fdbe8f77f6199ed46e188d'
        # sendDingTalk().question_down_image(accesskey)
        data = questionJobs.get_question_task_status(questionType=questionType, prj_id=prj_id)
        responseData = success.success_response()
        pageInfo = pageUtil.getPageInfo(data, page, pageSize)
        data_ = pageUtil.getDataInfo(data, page, pageSize)
        responseData['data'] = data_
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getquestionrepeatSteps(request):
    """
    获取问题步骤信息
    :param request:
    """
    if request.method == 'GET':
        questionID = request.GET.get('id')
        res = list(dataExploration_QuestionInfo.objects.filter(questionID=questionID).values('repeatSteps'))
        responseData = success.success_response()
        responseData['data'] = res
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getquestionhistory(request):
    """
    获取问题处理历史
    :param request:
    """
    if request.method == 'GET':
        questionID = request.GET.get('id')
        res = list(dataExploration_QuestionHandleHistory.objects.filter(questionID=questionID).values())
        responseData = success.success_response()
        responseData['data'] = res
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getprojectmodule(request):
    """
    获取项目模块
    :param request:
    """
    if request.method == 'GET':
        # print(request)
        project_id = request.GET.get('0')
        # print(project_id)
        res = list(Module.objects.filter(project_id=project_id, is_delete=0).values())
        # print(res)
        responseData = success.success_response()
        responseData['data'] = res
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def questionsenddingtalk(request):
    """
    线上问题发送钉钉消息
    :param request:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        questionTitle = requestData['questionTitle']
        at_mobiles = requestData['currentAssignmentPhone']
        currentAssignment = requestData['currentAssignment']
        prj_name = requestData['prj_name']
        handler = requestData['handler']
        handleType = requestData['handleType']
        prj_id = requestData['prj_id']
        comment = requestData['comment']
        # Type = requestData['Type']
        # Typedes = requestData['Typedes']
        DingTalk = sendDingTalk()
        webhooklist = DingTalk.get_project_robot(prj_id)
        at_mobileslist = []
        if at_mobiles is not None:
            at_mobileslist.append(at_mobiles)
        for webhook in webhooklist:
            DingTalk.send_online_question_assign(webhook, prj_name, at_mobileslist, questionTitle, handler,
                                                 currentAssignment, handleType, comment)
        responseData = success.success_response()
        return JsonResponse(data=responseData, safe=False)


from dwebsocket.decorators import accept_websocket


@accept_websocket
def nowtimelog(request):
    if request.is_websocket():
        # print(request.is_websocket())
        # request.websocket.send('123456'.encode('utf-8'))
        with open(r'/data/ncarzone/bigdata/out.log', 'r', encoding='UTF-8') as f:
            log_length = len(f.readlines())
            time.sleep(1)
        x = True
        while x:
            with open(r'/data/ncarzone/bigdata/out.log', 'r', encoding='UTF-8') as f:
                contents = f.readlines()
                length_tmp = len(contents)
            for i in range(log_length, length_tmp):
                request.websocket.send(contents[i].encode('UTF-8'))
                if '探查结束' in str(contents[i]):
                    x = False
            log_length = length_tmp
            time.sleep(1)


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from data_monior.dataworksCrawler.Run_Job import run_job
# from data_monior.dataworksTableCheck.servers.blink_RT_Task import RT_Task
import datetime


#
def twelve_time_job():
    '''
    每天十二点任务
    :return:
    '''
    run_job(user, password).run_job_twelve_time()


def eight_thirty_job():
    '''
    每天早上8点30任务
    :return:
    '''
    run_job(user, password).run_job_eight_thirty_time()


def send_ding_job():
    '''
    每天早上9点任务
    :return:
    '''
    # 4082f4dfda66f77cfb525561bd14fd208422bc18a3b6d499ffe9f8e7ad571297
    # 13c116808bdad57287301210fb9a370b454f39fdeb780e393053faba440b95b8 测试
    # dde17b9fca4cf4433840883d0bb527502cc51242770442039f2cc78977938069 线上问题
    # accesskey = '94e4dca163499d8e760440493e040dd9b7c6bb4d88fdbe8f77f6199ed46e188d'  # 数据监控
    # questionaccesskey = '94e4dca163499d8e760440493e040dd9b7c6bb4d88fdbe8f77f6199ed46e188d'  # 车辆管家线上问题
    # at_mobiles = []
    # prj_id_list = [9,1]
    # prj_id_dict = {'car':9,''}
    # DingTalk = sendDingTalk()
    # for prj_id in prj_id_list:
    #     webhooklist = DingTalk.get_project_robot(prj_id)
    #     for webhook in webhooklist:
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=4082f4dfda66f77cfb525561bd14fd208422bc18a3b6d499ffe9f8e7ad571297'
    sendDingTalk().send_online_question()
    sendDingTalk(file_name='dataworks').send_dataworks_alarm_rules(webhook)


def five_minute_job():
    '''
    每天早上9点-晚上7点，5分钟轮询任务 fe2c6fe467325529e24fee81721e9dbc64fcb636e9fa2111fdd2482ad4e99da3
    :return:
    '''
    # logger.info('blink实时监控任务')
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=4082f4dfda66f77cfb525561bd14fd208422bc18a3b6d499ffe9f8e7ad571297'
    at_mobiles = ['17600035316']
    blink = RT_Task()
    blink.run(webhook=webhook, at_mobiles=at_mobiles)
    # questionJobs.get_Lead_warehouse_question(user, password,accesskey)


def getOnlineQuestion():
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=4082f4dfda66f77cfb525561bd14fd208422bc18a3b6d499ffe9f8e7ad571297'
    questionJobs.get_Lead_warehouse_question(user, password, webhook)

#
# #
# a = 0
# while True:
#     if a < 1:
#         # nine_job()
#         eight_thirty_job()  # run_job_twelve_time()  run_job_eight_thirty_time
#         print('--------任务执行结束--------')
#         a += 1
#
# def job_listener(Event):
#     job = sched.get_job(Event.job_id)
#     # print(Event.job_id,job.id)
#     logger.info(job)
#     args = job.args
#     # 正常结束任务
#     if not Event.exception:
#         # logger.info('*' * 20, '成功', '*' * 20)
#         # logger.info(str(job), str(args))
#         # print('*' * 20, '成功', '*' * 20)
#         # print(job,args)
#         run_log.objects.create(job_name=job.id, run_date='',
#                                st_time='',
#                                end_time='',
#                                run_time=Event.scheduled_run_time,
#                                res='成功'
#                                )
#         # 恢复原先的任务定时时间
#         # sched.reschedule_job(Event.job_id, trigger='cron', hour='00', minute='10', second='00')
#         # for job in sched.get_jobs():
#         #     logger.info(job)
#         #     # print(job)
#         #     # print(job.name)
#         #     # print(job.trigger)
#     else:
#         # 计算当前时间5秒后的时间
#         # next_datetime = datetime.datetime.now() + datetime.timedelta(seconds=5)
#         # # 修改出现异常的任务的定时，重新计算下次执行时间，本例为5秒后
#         # sched.reschedule_job(Event.job_id, trigger='cron', hour=next_datetime.hour, minute=next_datetime.minute,
#         #                      second=next_datetime.second)
#         msg = f"jobname={job.name}|jobtrigger={job.trigger}|errcode={Event.code}|exception=[{Event.exception}]|traceback=[{Event.traceback}]|scheduled_time={Event.scheduled_run_time}"
#         run_log.objects.create(job_name=job.id, run_date='',
#                                st_time='',
#                                end_time='',
#                                run_time=Event.scheduled_run_time,
#                                res=str(msg)
#                                )
#         webhook = 'https://oapi.dingtalk.com/robot/send?access_token=94e4dca163499d8e760440493e040dd9b7c6bb4d88fdbe8f77f6199ed46e188d'
#         at_mobiles = ['15520608613']
#         DingTalk = sendDingTalk()
#         DingTalk.send_Error_Job(webhook, at_mobiles, job.id, Event.scheduled_run_time, str(msg))
#         logger.error(msg)
#
#
# # coalesce：当由于某种原因导致某个job积攒了好几次没有实际运行（比如说系统挂了5分钟后恢复，有一个任务是每分钟跑一次的，
# #           按道理说这5分钟内本来是“计划”运行5次的，但实际没有执行），如果coalesce为True，下次这个job被submit给executor时，
# #           只会执行1次，也就是最后这次，如果为False，那么会执行5次（不一定，因为还有其他条件，看后面misfire_grace_time的解释）
# # max_instance: 就是说同一个job同一时间最多有几个实例再跑，比如一个耗时10分钟的job，被指定每分钟运行1次，如果我们max_instance值为5，
# #               那么在第6~10分钟上，新的运行实例不会被执行，因为已经有5个实例在跑了
# # misfire_grace_time：设想和上述coalesce类似的场景，如果一个job本来14:00有一次执行，但是由于某种原因没有被调度上，现在14:01了，
# #           这个14:00的运行实例被提交时，会检查它预订运行的时间和当下时间的差值（这里是1分钟），大于我们设置的30秒限制，那么这个运行实例不会被执行。
#
# job_defaults = {
#     'coalesce': True,
#     'max_instances': 10,
#     'misfire_grace_time': 60
# }
# # 创建定时任务实例
# sched = BackgroundScheduler()
# sched.configure(job_defaults=job_defaults)
# # 添加任务1 获取存在规则的表
# sched.add_job(twelve_time_job, trigger='cron', hour='00', minute='00', second='00',
#               id="twelve_time_job")
# # 添加任务2 获取规则运行结果
# sched.add_job(eight_thirty_job, trigger='cron', hour='08', minute='30', second='00',
#               id='eight_thirty_job')
# # 添加任务3 发送钉钉群消息
# sched.add_job(send_ding_job, trigger='cron', hour='09', minute='00', second='00', id='nine_job')
# # # 添加任务4 发送钉钉群消息
# sched.add_job(send_ding_job, trigger='cron', hour='16', minute='00', second='00', id='four_job')
# # 添加任务5 每天早上9点-晚上12点，5分钟轮询任务
# sched.add_job(five_minute_job, trigger='cron', day_of_week='mon-fri', hour='9-18', minute='*/5', id='blink_job')
# # 添加任务5 每天24小时，1小时获取查询一次
# sched.add_job(getOnlineQuestion, trigger='cron', minute='*/30', id='getOnlineQuestion')
# # 创建监听，任务出错和任务正常结束都会执行job_listener函数
# sched.add_listener(job_listener, EVENT_JOB_ERROR | \
#                    EVENT_JOB_EXECUTED)
# # 开始定时任务
# sched.start()
