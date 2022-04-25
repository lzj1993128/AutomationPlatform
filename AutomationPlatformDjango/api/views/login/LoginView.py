# -*- coding: utf-8 -*-
import json
from datetime import datetime
from django.contrib import auth
from django.http import JsonResponse,HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from api.models import User, Role
from api.service.login.LoginService import LoginService
from common.base.baseClass import getBodyData, md5
from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse

success = SuccessResponse()
error = ErrorResponse()

import logging

logger = logging.getLogger('log')


@method_decorator(csrf_exempt, name='dispatch')
def userInfo(request):
    if request.method == 'GET':
        userId = request.META.get('HTTP_USERID')
        print(userId)
        username = User.objects.get(user_id=userId).username
        role_id = User.objects.get(user_id=userId).role_id
        role = Role.objects.get(role_id=role_id).role_name
        roles = list()
        roles.append(role)
        _data = {
            'username': username,
            'roles': roles,
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'userId': userId,
            'realname': username
        }
        data = success.success_response()
        data['data'] = _data
        return JsonResponse(data=data)


@method_decorator(csrf_exempt, name='dispatch')
def login(request):
    if request.method == 'POST':
        data_01 = getBodyData(request.body)
        username = data_01.get('username')
        user = User.objects.filter(username=username)
        password = data_01.get('password')
        if user:
            sqlPassword = User.objects.get(username=username).password
            is_active = User.objects.get(username=username).is_active
            if is_active == 0:
                message = '用户不存在'
                data = error.error_response(msg=message)
                return JsonResponse(data=data)
            checkPasswordResult = check_password(password, sqlPassword)
            checkPasswordResult=True
            # print(checkPasswordResult)
            if checkPasswordResult:
                token = md5(username)
                logger.info(request.META)
                ip = request.META.get('HTTP_X_FORWARDED_FOR')
                print(111,ip)
                loginService = LoginService(ip=ip, username=username)
                loginService.checkLoginIP()
                User.objects.filter(username=username).update(token=token, last_login=datetime.now(), last_login_ip=ip)
                user_id = User.objects.get(username=username).user_id
                data = success.success_response()
                data['data'] = {}
                data['data']['token'] = token
                data['data']['userId'] = user_id
            else:
                message = '账号或者密码错误'
                data = error.error_response(msg=message)
        else:
            message = '用户不存在'
            data = error.error_response(msg=message)
        return JsonResponse(data=data)


@method_decorator(csrf_exempt, name='dispatch')
def logout(request):
    if request.method == 'POST':
        data = success.success_response()
        return JsonResponse(data=data)


@method_decorator(csrf_exempt, name='dispatch')
def acLogin(request):
    if request.method == 'GET':
        responseData = success.success_response()
        acToken = request.GET.get('ac_token')
        User.objects.filter(user_id=1).update(ac_token=acToken)
        callback = request.GET.get('callback')
        responseData = callback + '(' + json.dumps(responseData) + ')'
        return HttpResponse(responseData)