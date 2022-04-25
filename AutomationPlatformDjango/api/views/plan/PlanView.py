import json
import threading
from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from api.exception.plan.PlanServiceException import LackMustRequestParam
from api.models import Plan, TaskHistory
from api.service.plan.PlanService import PlanService
from api.service.plan.SavePlanService import SavePlanService
from common.base.baseClass import getBodyData, isDictVuleNone
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
# from utils.CronUtil import CronUtil
from utils.DbUtil import DatabaseUtil
from utils.PageUtil import PageUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()


#  计划创建页，新增
@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def addPlan(request):
    try:
        if request.method == 'POST':
            requestData = getBodyData(request.body)
            savePlanService = SavePlanService()
            savePlanService.checkSaveRequestParam(requestData)
            plan_id = requestData.get('plan_id')
            planForm = requestData.get('planForm')
            plan_name = planForm.get('plan_name')
            description = planForm.get('description')
            is_enable = 1 if planForm.get('is_enable') else 0
            online_type = planForm.get('online_type')
            run_time_start = planForm.get('startTime')
            run_time_end = planForm.get('endTime')
            case_type = planForm.get('case_type')
            cron = planForm.get('cron')
            project_id = planForm.get('project_id')
            projectList = requestData.get('projectList')
            caseList = json.dumps(requestData.get('caseList'))
            envlist = requestData.get('envForm')
            dbList = requestData.get('dbList')
            rebotList = json.dumps(requestData.get('rebotList'))
            emailList = json.dumps(requestData.get('emailList'))
            msLogList = json.dumps(requestData.get('msLogList'))
            bigDataList = json.dumps(requestData.get('bigDataList'))
            if plan_id == '':
                plan = Plan(plan_name=plan_name, description=description, is_enable=is_enable, online_type=online_type,
                            run_time_start=run_time_start, run_time_end=run_time_end, projectList=projectList,
                            caseList=caseList, envList=envlist, emailList=emailList, msLogList=msLogList, cron=cron,
                            rebotList=rebotList, bigDataList=bigDataList, dbList=dbList, case_type=case_type,
                            project_id=project_id)
                plan.save()
            else:
                Plan.objects.filter(plan_id=plan_id).update(plan_name=plan_name, description=description,
                                                            online_type=online_type,
                                                            is_enable=is_enable, run_time_start=run_time_start,
                                                            run_time_end=run_time_end, projectList=projectList,
                                                            caseList=caseList, envList=envlist, emailList=emailList,
                                                            msLogList=msLogList, rebotList=rebotList, dbList=dbList,
                                                            bigDataList=bigDataList, case_type=case_type,
                                                            project_id=project_id, cron=cron,
                                                            update_time=datetime.now())
            responseData = success.success_response(msg='保存计划成功')
            return JsonResponse(data=responseData, safe=False)
    except LackMustRequestParam as e:
        responseData = error.error_response(msg=str(e))
        return JsonResponse(data=responseData, safe=False)


#  计划创建页，搜索
@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def searchPlan(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        if isDictVuleNone(requestData) is False:
            _data = Plan.objects.all().order_by('-update_time')
        else:
            plan_name = requestData.get('plan_name')
            _data = Plan.objects.filter(Q(plan_name__icontains=plan_name)).order_by('-update_time')
        fields = ['plan_id', 'plan_name', 'emailList', 'msLogList', 'is_enable', 'description', 'run_time_start',
                  'run_time_end', 'envList', 'run_status', 'online_type', 'rebotList', 'bigDataList', 'dbList',
                  'case_type', 'cron', 'project_id']
        _data = pageUtil.searchSqlFieldData(_data, fields)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def runPlan(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        plan_id = requestData.get('plan_id')
        envList = requestData.get('envList')
        dbList = requestData.get('dbList')
        responseData = success.success_response()
        plan = Plan.objects.filter(Q(run_status='1'), Q(is_enable=1), Q(is_delete='0'))
        if plan.count() > 0:
            msg = '有计划正在执行中，请稍后再执行'
            responseData['msg'] = msg
            return JsonResponse(data=responseData, safe=False)
        else:
            planService = PlanService(plan_id=plan_id, envList=envList, dbList=dbList)
            thread = threading.Thread(target=planService.runPlan)
            thread.start()
            return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def deletePlan(request):
    """
    删除计划
    :param request:
    :return:
    """
    if request.method == 'GET':
        plan_id = request.GET['plan_id']
        Plan.objects.filter(plan_id=plan_id).update(is_delete='1')
        data = success.success_response(msg='计划删除成功')
        return JsonResponse(data=data, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def editPlan(request):
    """
    编辑计划
    :param request:
    :return:
    """
    if request.method == 'GET':
        plan_id = request.GET['plan_id']
        _data = Plan.objects.filter(plan_id=plan_id)
        _data = pageUtil.searchSqlFieldData(_data)
        responseData = success.success_response()
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def handleCronExp(request):
    """
    处理cron表达式
    :param request:
    :return:
    """
    if request.method == 'GET':
        cron = request.GET['cron']
        try:
            _data = CronUtil().handleCron(cron)
            _desc = CronUtil().getCronDesc(cron)
            responseData = success.success_response()
            responseData['data'] = _data
            responseData['desc'] = _desc
            return JsonResponse(data=responseData, safe=False)
        except Exception:
            responseData = error.error_response()
            responseData['msg'] = '表达式不支持，请试试其他'
            return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def planRunHistory(request):
    if request.method == 'GET':
        planId = request.GET['plan_id']
        _data = TaskHistory.objects.filter(plan_id=planId).values('task_id', 'start_time', 'end_time',
                                                                  'run_time', 'run_result').order_by('-create_time')[:20]
        _data = pageUtil.searchSqlFieldData(_data)
        responseData = success.success_response()
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)
