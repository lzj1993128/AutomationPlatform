from datetime import datetime
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from common.base.baseClass import getBodyData

from Decorator.RequestDecorator import requestIntercept

from api.models import Env
from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from utils.PageUtil import PageUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def envAdd(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        env_id = requestData.get('env_id')
        env_name = requestData.get('env_name')
        env_url = requestData.get('env_url')
        env_type = requestData.get('env_type')
        if env_id == '':
            env = Env(env_name=env_name, env_url=env_url, env_type=env_type)
            env.save()
        else:
            Env.objects.filter(env_id=env_id).update(env_name=env_name, env_url=env_url, env_type=env_type, update_time=datetime.now())
        responseData = success.success_response(msg='保存环境成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def envSearch(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        if 'env_name' in requestData.keys():
            env_name = requestData.get('env_name')
            _data = Env.objects.filter(Q(env_name__icontains=env_name)).order_by('-update_time')
        else:
            _data = Env.objects.all().order_by('-update_time')
        fields = ['env_id', 'env_name', 'env_type', 'env_url', 'create_time', 'update_time']
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
def envDelete(request):
    """
    删除环境
    :param request:
    :return:
    """
    if request.method == 'GET':
        env_id = request.GET['env_id']
        Env.objects.filter(env_id=env_id).update(is_delete='1')
        data = success.success_response(msg='删除环境成功')
        return JsonResponse(data=data, safe=False)
