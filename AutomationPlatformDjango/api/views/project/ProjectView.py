# -*- coding: utf-8 -*-
from datetime import datetime

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from api.models import Project
from api.sqls.project.ProjectSql import *
from common.base.baseClass import getBodyData, isDictVuleNone, isNone
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
from utils.DbUtil import DatabaseUtil
from utils.PageUtil import PageUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def projectAdd(request):
    """
    项目增加
    :param request:
    :return:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        prj_id = requestData.get('prj_id')
        prj_name = requestData.get('prj_name')
        robot_group_id = requestData.get('robot_group_id') if 'robot_group_id' in requestData.keys() else None
        description = isNone(requestData.get('description'))
        if prj_id == '':
            prj = Project(prj_name=prj_name, description=description, robot_group_id=robot_group_id)
            prj.save()
        else:
            Project.objects.filter(prj_id=prj_id).update(prj_name=prj_name, description=description,robot_group_id=robot_group_id,
                                                         update_time=datetime.now())
        responseData = success.success_response(msg='项目保存成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def projectSearch(request):
    """
    项目搜索
    :param request:
    :return:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        prj_name = requestData.get('prj_name') if isDictVuleNone(requestData) else ''
        _data = dbUtil.sql_to_dict(ProjectSql1(prj_name=prj_name))
        _data = pageUtil.searchSqlFieldData(_data)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def projectUpdate(request):
    """
    项目更新
    :param request:
    :return:
    """
    if request.method == 'GET':
        prj_id = request.GET['prj_id']
        _data = Project.objects.filter(prj_id=prj_id)
        fields = ['prj_name', 'description']
        _data = pageUtil.searchSqlFieldData(_data, fields)[0]
        data = success.success_response()
        data['data'] = _data
        return JsonResponse(data=data, safe=False)
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        prj_id = requestData.get('prj_id')
        prj_name = requestData.get('prj_name')
        description = requestData.get('description')
        Project.objects.filter(prj_id=prj_id).update(prj_name=prj_name, description=description)
        data = success.success_response(msg='项目更新成功')
        return JsonResponse(data=data, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def projectDelete(request):
    """
    项目删除
    :param request:
    :return:
    """
    if request.method == 'GET':
        prj_id = request.GET['prj_id']
        Project.objects.filter(prj_id=prj_id).update(is_delete='1')
        data = success.success_response(msg='项目删除成功')
        return JsonResponse(data=data, safe=False)
