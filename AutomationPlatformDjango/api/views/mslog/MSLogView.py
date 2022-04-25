from datetime import datetime
import json

from api.models import MSLog

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from utils.PageUtil import PageUtil
from common.base.baseClass import getBodyData

from utils.DbUtil import DatabaseUtil
from api.sqls.mslog.MSLogViewSql import *

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()


@method_decorator(csrf_exempt, name='dispatch')
def addMSLog(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        ms_id = requestData.get('ms_id')
        project_id = requestData.get('project')
        module_id = requestData.get('module')
        ms_name = requestData.get('ms_name')
        ms_ip = requestData.get('ms_ip')
        ms_port = requestData.get('ms_port')
        ms_user = requestData.get('ms_user')
        ms_password = requestData.get('ms_password')
        ms_log_list = json.dumps(requestData.get('mslogList'))
        if ms_id == '':
            msl = MSLog(ms_name=ms_name, project_id=project_id, module_id=module_id, ms_ip=ms_ip,
                        ms_password=ms_password, ms_port=ms_port, ms_user=ms_user, ms_log_list=ms_log_list)
            msl.save()
        else:
            MSLog.objects.filter(ms_id=ms_id).update(ms_name=ms_name, project_id=project_id, module_id=module_id,
                                                     ms_ip=ms_ip, ms_password=ms_password, ms_port=ms_port,
                                                     ms_user=ms_user, ms_log_list=ms_log_list, update_time=datetime.now())
        responseData = success.success_response(msg='保存微服务成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
def searchMSLog(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        ms_name = requestData.get('ms_name')
        _data = dbUtil.sql_to_dict(MSLogSql(ms_name))
        _data = pageUtil.searchSqlFieldData(_data)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
def deleteMSLog(request):
    """
    删除计划
    :param request:
    :return:
    """
    if request.method == 'GET':
        ms_id = request.GET['ms_id']
        MSLog.objects.filter(ms_id=ms_id).update(is_delete='1')
        data = success.success_response(msg='微服务删除成功')
        return JsonResponse(data=data, safe=False)
