from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from api.models import User
from api.service.user.UserService import UserService
from common.base.baseClass import getBodyData
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
from utils.PageUtil import PageUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def userAdd(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        role_id = requestData.get('role_id')
        username = requestData.get('username')
        user_id = requestData.get('user_id')
        nickname = requestData.get('nickname')
        is_active = requestData.get('is_active')
        is_active = 1 if is_active else 0
        password = requestData.get('password')
        phone = requestData.get('phone')
        makePassword = make_password(password, None, 'pbkdf2_sha256')
        if user_id == '':
            userService = UserService()
            msg = userService.savaUser(username=username, role_id=role_id, password=makePassword, nickname=nickname,
                                       phone=phone)
        else:
            User.objects.filter(user_id=user_id).update(username=username, role_id=role_id,
                                                        is_active=is_active, nickname=nickname, phone=phone,
                                                        update_time=datetime.now())
            msg = '更新用户成功'
        responseData = success.success_response(msg=msg)
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def userSearch(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        if 'username' in requestData.keys():
            username = requestData.get('username')
            _data = User.objects.filter(Q(username__icontains=username))
        else:
            _data = User.objects.all()
        fields = ['user_id', 'role_id', 'create_time', 'is_superuser', 'username', 'is_active', 'nickname', 'phone']
        _data = pageUtil.searchSqlFieldData(_data, fields)
        responseData = success.success_response()
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData['pageInfo'] = pageInfo
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def passwordUpdate(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        password = requestData.get('password')
        if not password:
            responseData = error.error_response(msg='请检查下密码输入')
            return JsonResponse(data=responseData, safe=False)
        makePassword = make_password(password, None, 'pbkdf2_sha256')
        user_id = requestData.get('user_id')
        User.objects.filter(user_id=user_id).update(password=makePassword, update_time=datetime.now())
        responseData = success.success_response(msg='修改成功')
        return JsonResponse(data=responseData, safe=False)
