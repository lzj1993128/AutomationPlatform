import json
import logging
import os
import threading
from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from AutomationPlatformDjango import settings
from Decorator.RequestDecorator import requestIntercept
from api.models import Interface, User
from api.models import Project
from api.service.excelImport.InterfaceExcelService import ExcelService
from api.sqls.interface.InterfaceViewSql import *
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
def interfaceAdd(request):
    """
    增加接口
    :param request:
    :return:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        requestForm = requestData.get('requestForm')
        api_url = requestForm.get('api_url')
        opt_type = requestForm.get('opt_type')
        api_name = requestForm.get('api_name')
        method = requestForm.get('method')
        data_type = requestForm.get('data_type')
        description = requestForm.get('description')
        request_method = requestForm.get('request_method')
        requestJsonList = requestForm.get('requestJsonList')
        requestJsonList = str(json.dumps(requestJsonList)) if requestJsonList else []
        zk_database = requestForm.get('zk_database')
        zk_api_name = requestForm.get('zk_api_name')
        zk_api_method = isNone(requestForm.get('zk_api_method'))
        api_url = api_url if request_method == 'http' else zk_api_method
        request_header_param = requestData.get('requestHeaderList')
        request_header_param = str(json.dumps(request_header_param)) if request_header_param else None
        request_body_param = requestData.get('requestBodyList')
        request_body_param = str(json.dumps(request_body_param)) if request_body_param else None
        project_id = requestData.get('projectForm')
        module_id = requestData.get('moduleForm')
        userId = request.META.get('HTTP_USERID')
        username = User.objects.get(user_id=userId).username
        is_sign = requestForm.get('is_sign')
        if opt_type == 'edit':
            api_id = requestForm.get('api_id')
            Interface.objects.filter(api_id=api_id).update(api_name=api_name, api_url=api_url, method=method,
                                                           data_type=data_type, description=description,
                                                           request_header_param=request_header_param,
                                                           request_body_param=request_body_param,
                                                           request_method=request_method,
                                                           zk_database=zk_database,
                                                           zk_api_name=zk_api_name,
                                                           requestJsonList=requestJsonList,
                                                           project_id=project_id, module_id=module_id,
                                                           is_sign=is_sign,
                                                           update_time=datetime.now())
            responseData = success.success_response(msg='接口保存成功')
            return JsonResponse(responseData, safe=False)
        else:
            if Interface.objects.filter(
                    Q(zk_api_name=zk_api_name) & Q(api_url=api_url) & Q(
                        is_delete='0') & Q(method=method)):
                responseData = success.success_response(msg='接口已存在，请勿重复添加')
                return JsonResponse(responseData, safe=False)
            else:
                if opt_type == 'copy':
                    api_id = requestForm.get('api_id')
                    api = Interface.objects.get(pk=api_id)
                    api.pk = None
                    api = Interface(api_name=api_name, api_url=api_url, method=method, data_type=data_type,
                                    description=description, creator=username,
                                    request_header_param=request_header_param,
                                    request_body_param=request_body_param,
                                    request_method=request_method,
                                    zk_database=zk_database,
                                    zk_api_name=zk_api_name,
                                    requestJsonList=requestJsonList,
                                    project_id=project_id, module_id=module_id, is_sign=is_sign)
                    api.save()
                else:

                    api = Interface(api_name=api_name, api_url=api_url, method=method, data_type=data_type,
                                    description=description, creator=username,
                                    request_header_param=request_header_param,
                                    request_body_param=request_body_param,
                                    request_method=request_method,
                                    zk_database=zk_database,
                                    zk_api_name=zk_api_name,
                                    requestJsonList=requestJsonList,
                                    project_id=project_id, module_id=module_id, is_sign=is_sign)
                    api.save()
                responseData = success.success_response(msg='接口保存成功')
                return JsonResponse(responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getPrjectInfo(request):
    """
    获取项目信息
    :param request:
    :return:
    """
    if request.method == 'GET':
        _data = Project.objects.all()
        fields = ['prj_id', 'prj_name']
        _data = pageUtil.searchSqlFieldData(_data, fields=fields)
        responseData = success.success_response(msg='获取项目信息成功')
        responseData['data'] = _data
        return JsonResponse(responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def interfaceSearch(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        api_name = isNone(requestData.get('api_name'))
        api_url = isNone(requestData.get('api_url'))
        method = isNone(requestData.get('method'))
        requestMethod = isNone(requestData.get('requestMethod'))
        project_id = isNone(requestData.get('prj_id'))
        module_id = isNone(requestData.get('module_id'))
        _data = dbUtil.sql_to_dict(
            InterfaceSql1(api_name, api_url, method, project_id, module_id, requestMethod))
        # 查找数据库
        _data = pageUtil.searchSqlFieldData(_data)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def interfaceSearchById(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        api_id = requestData.get('api_id')
        _data = dbUtil.sql_to_dict(InterfaceSql2(api_id))
        _data = pageUtil.searchSqlFieldData(_data)
        responseData = success.success_response()
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def interfaceDelete(request):
    """接口删除"""
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        api_id = requestData.get('api_id')
        Interface.objects.filter(api_id=api_id).update(is_delete='1')
        responseData = success.success_response(msg='删除接口成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
# @requestIntercept
def uploadImportExcel(request):
    """
    上传文件表格接口
    :param request:
    :return:
    """
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            responseData = success.success_response(msg='没有检测到没有上传文件，请确认')
            return JsonResponse(data=responseData, safe=False)
        else:
            f = open(os.path.join(settings.job_path, file.name), 'wb+')
            for chunk in file.chunks():
                f.write(chunk)
            f.close()
            userId = request.META.get('HTTP_USERID') if request.META.get('HTTP_USERID') else 3
            excelService = ExcelService(os.path.join(settings.job_path, file.name), userId)
            thread = threading.Thread(target=excelService.addRowData)
            thread.start()
            responseData = success.success_response(msg='导入请求成功')
            return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def downloadImportExcel(request):
    if request.method == 'GET':
        type = request.GET['type']
        if type == 'add':
            file_name = os.path.join(settings.excel_path, 'api_add_demo.xlsx')
            file = open(file_name, 'rb')
        else:
            file_name = os.path.join(settings.excel_path, 'api_add_demo.xlsx')
            file = open(file_name, 'rb')
        return FileResponse(file)
