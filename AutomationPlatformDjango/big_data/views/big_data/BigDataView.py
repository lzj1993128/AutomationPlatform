import logging
import threading
from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from api.models import User
from big_data.exception.big_data.BigDataRequestException import RequestException
from big_data.models import BigData
from big_data.service.big_data.BigDataCompareService import BigDataComepareService
from big_data.service.big_data.TestRunRequest import TestRunRequest
from big_data.sqls.big_data.BigDataSql import *
from common.base.baseClass import getBodyData, isNone
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
from utils.DbUtil import DatabaseUtil
from utils.PageUtil import PageUtil

logger = logging.getLogger('log')

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def addBigData(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        big_data_id = requestData.get('big_data_id')
        big_data_name = requestData.get('big_data_name')
        project = requestData.get('project_id')
        module = requestData.get('module_id')
        db = requestData.get('db_id')
        request_method = requestData.get('request_method')
        api_name = requestData.get('api_name')
        api_url = requestData.get('api_url')
        method = requestData.get('method')
        data_type = requestData.get('data_type')
        requestHeader = requestData.get('requestHeader')
        requestBody = requestData.get('requestBody')
        requestCompareFieldList = requestData.get('requestCompareFieldList')
        zk_database = requestData.get('zk_database')
        zk_api_name = requestData.get('zk_api_name')
        zk_api_method = requestData.get('zk_api_method')
        requestJson = requestData.get('requestJson')
        reponse_field = requestData.get('reponse_field')
        report_database_name = requestData.get('report_database_name')
        sql = requestData.get('sql')
        description = requestData.get('description')
        userId = request.META.get('HTTP_USERID')
        username = User.objects.get(user_id=userId).username
        opt_type = requestData.get('opt_type')
        if opt_type == 'add':
            big_data = BigData(big_data_name=big_data_name, project_id=project, module_id=module, db_id=db,
                               request_method=request_method, api_name=api_name, api_url=api_url, method=method,
                               data_type=data_type, requestHeader=requestHeader, requestBody=requestBody,
                               requestCompareFieldList=requestCompareFieldList,
                               zk_database=zk_database, zk_api_name=zk_api_name,
                               zk_api_method=zk_api_method, requestJson=requestJson, reponse_field=reponse_field,
                               report_database_name=report_database_name,
                               sql=sql, description=description, creator=username, last_updata_person=username)
            big_data.save()
        if opt_type == 'edit':
            BigData.objects.filter(big_data_id=big_data_id).update(big_data_name=big_data_name, project_id=project,
                                                                   module_id=module, db_id=db,
                                                                   request_method=request_method, api_name=api_name,
                                                                   api_url=api_url, method=method,
                                                                   data_type=data_type, requestHeader=requestHeader,
                                                                   requestBody=requestBody,
                                                                   requestCompareFieldList=requestCompareFieldList,
                                                                   zk_api_name=zk_api_name,
                                                                   zk_database=zk_database, zk_api_method=zk_api_method,
                                                                   requestJson=requestJson,
                                                                   reponse_field=reponse_field,
                                                                   report_database_name=report_database_name,
                                                                   sql=sql, description=description,
                                                                   last_updata_person=username,
                                                                   update_time=datetime.now())
        if opt_type == 'copy':
            big_data = BigData.objects.get(pk=big_data_id)
            big_data.pk = None
            big_data = BigData(big_data_name=big_data_name, project_id=project, module_id=module, db_id=db,
                               request_method=request_method, api_name=api_name, api_url=api_url, method=method,
                               data_type=data_type, requestHeader=requestHeader, requestBody=requestBody,
                               requestCompareFieldList=requestCompareFieldList, zk_database=zk_database,
                               zk_api_name=zk_api_name,
                               zk_api_method=zk_api_method,
                               requestJson=requestJson, reponse_field=reponse_field,
                               report_database_name=report_database_name,
                               sql=sql, description=description, creator=username, last_updata_person=username)
            big_data.save()
        responseData = success.success_response(msg='保存成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getBigData(request):
    """
    通过big_data_id获取已经保存的big_data
    :param request:
    :return:
    """
    if request.method == 'GET':
        big_data_id = request.GET['big_data_id']
        _data = BigData.objects.filter(big_data_id=big_data_id)
        _data = pageUtil.searchSqlFieldData(_data)[0]
        responseData = success.success_response()
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def searchBigData(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        big_data_name = requestData.get('big_data_name')
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        project_id = isNone(requestData.get('prj_id'))
        module_id = isNone(requestData.get('module_id'))
        _data = dbUtil.sql_to_dict(bigDataSearchSql(big_data_name, project_id, module_id))
        _data = pageUtil.searchSqlFieldData(_data)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def runBigDataCompare(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        big_data_id = requestData.get('big_data_id')
        envList = requestData.get('envForm')
        responseData = success.success_response()
        bigData = BigData.objects.filter(Q(run_status='1'), Q(is_delete='0'))
        if bigData.count() > 0:
            msg = '有比较接口正在执行中，请稍后再执行'
            responseData['msg'] = msg
            return JsonResponse(data=responseData, safe=False)
        else:
            bigDataComepareService = BigDataComepareService(big_data_id, envList)
            thread = threading.Thread(target=bigDataComepareService.doRequestCompareFieldList)
            thread.start()
            return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def deleteBigData(request):
    """
    删除大数据记录
    :param request:
    :return:
    """
    if request.method == 'GET':
        big_data_id = request.GET['big_data_id']
        BigData.objects.filter(big_data_id=big_data_id).update(is_delete='1')
        data = success.success_response(msg='删除成功')
        return JsonResponse(data=data, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def testRunRequest(request):
    """
    调试请求
    :return:
    """
    try:
        if request.method == 'POST':
            requestData = getBodyData(request.body)
            testRunRequest = TestRunRequest(requestData)
            data = testRunRequest.runTest()
            responseData = success.success_response()
            responseData['data'] = data
            return JsonResponse(data=responseData, safe=False)
    except RequestException as e:
        responseData = error.error_response(msg=str(e))
        responseData['data'] = str(e)
        return JsonResponse(data=responseData, safe=False)
