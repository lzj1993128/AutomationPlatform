from datetime import datetime
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from common.base.baseClass import getBodyData
from Decorator.RequestDecorator import requestIntercept

from api.models import Email
from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from utils.PageUtil import PageUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def emailAdd(request):
    """
    新增和编辑收件邮箱
    :param request:
    :return:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        email_id = requestData.get('email_id')
        email_name = requestData.get('email_name')
        email_address = requestData.get('email_address')
        if email_id == '':
            email = Email(email_name=email_name, email_address=email_address)
            email.save()
        else:
            Email.objects.filter(email_id=email_id).update(email_name=email_name, email_address=email_address,
                                                           update_time=datetime.now())
        responseData = success.success_response(msg='保存邮箱成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def emailSearch(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        if 'email_name' in requestData.keys():
            email_name = requestData.get('email_name')
            _data = Email.objects.filter(Q(email_name__icontains=email_name) & Q(email_type=0)).order_by('-update_time')
        else:
            _data = Email.objects.filter(Q(email_type=0)).order_by('-update_time')
        fields = ['email_id', 'email_name', 'email_address', 'email_type']
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
def emailDelete(request):
    """
    删除邮箱
    :param request:
    :return:
    """
    if request.method == 'GET':
        email_id = request.GET['email_id']
        Email.objects.filter(email_id=email_id).update(is_delete='1')
        data = success.success_response(msg='删除邮箱成功')
        return JsonResponse(data=data, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def emailSendEmail(request):
    if request.method == 'GET':
        _data = Email.objects.filter(email_type='1')
        _data = pageUtil.searchSqlFieldData(_data)
        data = success.success_response()
        data['data'] = _data
        return JsonResponse(data=data, safe=False)

    if request.method == 'POST':
        requestData = getBodyData(request.body)
        email_id = requestData.get('email_id')
        email_name = requestData.get('email_name')
        email_address = requestData.get('email_address')
        email_password = requestData.get('email_password')
        smtp_address = requestData.get('smtp_address')
        smtp_port = requestData.get('smtp_port')
        if email_id == '':
            email = Email(email_name=email_name, email_address=email_address, email_password=email_password,
                          smtp_address=smtp_address, smtp_port=smtp_port, email_type='1')
            email.save()
        else:
            Email.objects.filter(email_id=email_id).update(email_name=email_name, email_address=email_address,
                                                           email_password=email_password,
                                                           smtp_address=smtp_address, smtp_port=smtp_port,
                                                           email_type='1')
        responseData = success.success_response(msg='保存邮箱成功')
        return JsonResponse(data=responseData, safe=False)
