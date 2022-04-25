from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from api.models import Business
from common.base.baseClass import getBodyData
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
from utils.PageUtil import PageUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def businessAdd(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        bd_id = requestData.get('bd_id')
        bd_name = requestData.get('bd_name')
        description = requestData.get('description')
        if bd_id == '':
            business = Business(bd_name=bd_name, description=description)
            business.save()
        else:
            Business.objects.filter(bd_id=bd_id).update(bd_name=bd_name, description=description,
                                                        update_time=datetime.now())
        responseData = success.success_response(msg='保存成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def businessSearch(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        if 'bd_name' in requestData.keys():
            bd_name = requestData.get('bd_name')
            _data = Business.objects.filter(Q(bd_name__icontains=bd_name)).order_by('-update_time')
        else:
            _data = Business.objects.all().order_by('-update_time')
        fields = ['bd_id', 'bd_name', 'description', 'create_time', 'update_time']
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
