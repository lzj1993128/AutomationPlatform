from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from api.models import Params
from common.base.baseClass import getBodyData
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
from utils.PageUtil import PageUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def paramAdd(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        param_id = requestData.get('param_id')
        param_name = requestData.get('param_name')
        param_type = requestData.get('param_type')
        description = requestData.get('description')
        param_list = requestData.get('param_list')
        userId = request.META.get('HTTP_USERID')
        if param_id == '':
            param = Params(param_name=param_name, param_type=param_type, description=description, param_list=param_list,
                         creator=userId, update_person=userId)
            param.save()
        else:
            Params.objects.filter(param_id=param_id).update(param_name=param_name, param_type=param_type,
                                                            description=description, param_list=param_list,
                                                            update_person=userId, update_time=datetime.now())
        responseData = success.success_response(msg='保存成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def paramSearch(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        if 'param_name' in requestData.keys():
            param_name = requestData.get('param_name')
            _data = Params.objects.filter(Q(param_name__icontains=param_name)).order_by('-update_time')
        else:
            _data = Params.objects.all().order_by('-update_time')
        fields = ['param_id', 'param_name', 'param_type', 'description', 'param_list', 'create_time', 'update_time']
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
