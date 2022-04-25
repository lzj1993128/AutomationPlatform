from api.models import Module
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q

from Decorator.RequestDecorator import requestIntercept
from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from utils.PageUtil import PageUtil
from common.base.baseClass import getBodyData

from api.service.module.ModuleService import ModuleService

import logging

logger = logging.getLogger('log')

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def moduleSeach(request):
    if request.method == 'GET':
        prj_id = request.GET['prj_id']
        try:
            module_name = request.GET['moduleName']
        except Exception as e:
            logger.error('说明没有传module名称，module_name置为空')
            module_name = ''
        _data = Module.objects.filter(Q(project_id=prj_id) & Q(module_name__startswith=module_name)).order_by('-update_time')
        fields = ['module_id', 'module_name']
        _data = pageUtil.searchSqlFieldData(_data, fields=fields)
        responseData = success.success_response(msg='获取模块信息成功')
        responseData['data'] = _data
        return JsonResponse(responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def moduleAdd(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        prj_id = requestData.get('prj_id')
        moduleData = requestData.get('module_name')
        moduleService = ModuleService(prj_id, moduleData)
        result = moduleService.saveModule()
        responseData = success.success_response(msg=result)
        return JsonResponse(responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def moduleDelete(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        module_id = requestData.get('module_id')
        Module.objects.filter(module_id=module_id).update(is_delete='1')
        responseData = success.success_response(msg='删除模块成功')
        return JsonResponse(responseData, safe=False)
