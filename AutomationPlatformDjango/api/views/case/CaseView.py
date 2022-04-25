import json
from api.models import Case
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from Decorator.RequestDecorator import requestIntercept
from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from utils.PageUtil import PageUtil
from common.base.baseClass import getBodyData, isNone
from api.service.case.CaseService import CaseService
from api.service.case.CaseTreeService import CaseTreeService
from api.service.case.SaveCaseService import SaveCaseService
from api.exception.plan.PlanServiceException import LackMustRequestParam

from utils.DbUtil import DatabaseUtil
from api.sqls.case.CaseViewSql import *
import logging

logger = logging.getLogger('log')

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()
caseTreeService = CaseTreeService()


# 用例管理页搜索
@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def caseCreatCaseSearch(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        if 'bd_id' in requestData.keys():
            bd_id = requestData.get('bd_id')
        else:
            bd_id = ''
        case_name = isNone(requestData.get('case_name'))
        project_id = isNone(requestData.get('caseProject'))
        module_id = isNone(requestData.get('selectModule'))
        case_type = isNone(requestData.get('case_type'))
        online_type = isNone(requestData.get('online_type'))
        api_list = isNone(requestData.get('api_list'))
        _data = dbUtil.sql_to_dict(CaseSql1(case_name, case_type, project_id, module_id, online_type, api_list, bd_id))
        _data = pageUtil.searchSqlFieldData(_data)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getCaseTree(request):
    if request.method == 'GET':
        caseTreeData = caseTreeService.getCaseTree()
        responseData = success.success_response()
        responseData['caseTreeData'] = caseTreeData
        return JsonResponse(data=responseData, safe=False)


#  用例创建页，新增用例
@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def addTestCase(request):
    try:
        if request.method == 'POST':
            requestData = getBodyData(request.body)
            userId = request.META.get('HTTP_USERID')
            saveCaseService = SaveCaseService()
            saveCaseService.checkSaveRequestParam(requestData)
            saveCaseService.saveCase(requestData, userId)
            responseData = success.success_response(msg='保存用例成功')
            return JsonResponse(data=responseData, safe=False)
    except LackMustRequestParam as e:
        responseData = error.error_response(msg=str(e))
        return JsonResponse(data=responseData, safe=False)


# 用例创建页，用例编辑
@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def editTestCase(request):
    if request.method == 'GET':
        case_id = request.GET['case_id']
        _data = Case.objects.filter(case_id=case_id, is_delete='0')
        if _data:
            _data = pageUtil.searchSqlFieldData(_data)[0]
            responseData = success.success_response()
            responseData['data'] = _data
        else:
            responseData = error.error_response('用例已经被删除')
        # 将用例步骤进行特殊的数据处理
        return JsonResponse(data=responseData, safe=False)


# 用例创建页，用例删除
@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def deleteTestCase(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        case_id = requestData.get('case_id')
        Case.objects.filter(case_id=case_id).update(is_delete='1')
        responseData = success.success_response(msg='删除成功')
        return JsonResponse(data=responseData, safe=False)


# 用例创建页，用例执行
@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def caseRunTestCase(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        stepsForm = None
        if 'stepsForm' in requestData.keys():
            stepsForm = requestData.get('stepsForm')
        case_id = None
        if 'case_id' in requestData.keys():
            case_id = requestData.get('case_id')
        envForm = requestData.get('envForm')
        caseService = CaseService(stepsForm, envForm, case_id)
        result = caseService.run_case()
        responseData = success.success_response()
        responseData['caseResult'] = result
        return JsonResponse(data=responseData, safe=False)
