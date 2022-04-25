from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from api.models import Robot
from api.service.robot.RobotService import RobotService
from common.base.baseClass import getBodyData
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
from utils.PageUtil import PageUtil

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def addRebot(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        userId = request.META.get('HTTP_USERID')
        opt_type = requestData['opt_type']
        if opt_type == 'add':
            RobotService().saveRebot(requestData, userId)
        else:
            RobotService().editRobot(requestData, userId)
        responseData = success.success_response(msg='保存成功')
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def searchRebot(request):
    """
    搜索群组
    :param request:
    :return:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        group_name = requestData['group_name'] if 'group_name' in requestData.keys() else ''
        _data = Robot.objects.filter(group_name__contains=group_name, is_delete='0', type=1).values('robot_id',
                                                                                                    'group_name',
                                                                                                    'type',
                                                                                                    'create_time').order_by(
            'create_time')
        _data = pageUtil.searchSqlFieldData(_data)
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
def searchALLRebot(request):
    """
    搜索所有机器人接口
    :param request:
    :return:
    """
    if request.method == 'POST':
        _data = Robot.objects.filter(is_delete='0', type=2).values()
        _data = pageUtil.searchSqlFieldData(_data)
        responseData = success.success_response()
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def getById(request):
    if request.method == 'GET':
        robot_id = request.GET['robot_id']
        _data = Robot.objects.filter(p_id=robot_id, is_delete='0', type=2).values('robot_id', 'group_name', 'type',
                                                                                  'p_id',
                                                                                  'create_time', 'robot_name',
                                                                                  'keywordList',
                                                                                  'web_hook')
        _data = pageUtil.searchSqlFieldData(_data)
        responseData = success.success_response()
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def robotDelete(request):
    """
    机器人删除
    :param request:
    :return:
    """
    if request.method == 'GET':
        robot_id = request.GET['robot_id']
        Robot.objects.filter(robot_id=robot_id).update(is_delete='1')
        data = success.success_response(msg='机器人删除成功')
        return JsonResponse(data=data, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def groupDelete(request):
    """
    群组删除
    :param request:
    :return:
    """
    if request.method == 'GET':
        robot_id = request.GET['robot_id']
        Robot.objects.filter(robot_id=robot_id).update(is_delete='1')
        Robot.objects.filter(p_id=robot_id).update(is_delete='1')
        data = success.success_response(msg='群组删除成功')
        return JsonResponse(data=data, safe=False)
