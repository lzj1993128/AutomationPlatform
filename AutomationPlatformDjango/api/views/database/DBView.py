from datetime import datetime
import json

from api.models import Database

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import method_decorator
from django.db.models import Q

from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from utils.PageUtil import PageUtil
from Decorator.RequestDecorator import requestIntercept
from common.base.baseClass import getBodyData

from utils.DbUtil import DatabaseUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def addDB(request):
    requestData = getBodyData(request.body)
    db_id = requestData.get('db_id')
    db_name = requestData.get('db_name')
    db_host = requestData.get('db_host')
    db_port = requestData.get('db_port')
    db_user = requestData.get('db_user')
    db_type = requestData.get('db_type')
    db_passwd = requestData.get('db_passwd')
    connect_name = requestData.get('connect_name')
    # makePassword = make_password(db_passwd, None, 'pbkdf2_sha256')
    if db_id == '':
        msl = Database(connect_name=connect_name, db_name=db_name, db_host=db_host, db_port=db_port, db_user=db_user, db_passwd=db_passwd,db_type=db_type)
        msl.save()
    else:
        Database.objects.filter(db_id=db_id).update(connect_name=connect_name, db_name=db_name, db_host=db_host, db_port=db_port, db_user=db_user,db_type=db_type,
                                                    db_passwd=db_passwd, update_time=datetime.now())
    responseData = success.success_response(msg='保存服务器成功')
    return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispath')
@requestIntercept
def searchDB(request):
    requestData = getBodyData(request.body)
    db_name = requestData.get('db_name')
    _data = Database.objects.filter(Q(is_delete='0') & Q(db_name__contains=db_name))
    fields = ['connect_name', 'db_id', 'db_name', 'db_host', 'db_port', 'db_user','db_type']
    _data = pageUtil.searchSqlFieldData(_data, fields)
    responseData = success.success_response()
    if 'page' in requestData.keys():
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData['pageInfo'] = pageInfo
    responseData['data'] = _data
    return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def deleteDB(request):
    """
    删除计划
    :param request:
    :return:
    """
    if request.method == 'GET':
        db_id = request.GET['db_id']
        Database.objects.filter(db_id=db_id).update(is_delete='1')
        data = success.success_response(msg='服务器删除成功')
        return JsonResponse(data=data, safe=False)
