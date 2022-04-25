import os, time

from django.db.models import Q
from api.models import Jobs
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from AutomationPlatformDjango import settings

from Decorator.RequestDecorator import requestIntercept
from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from utils.PageUtil import PageUtil
from common.base.baseClass import getBodyData, isDictVuleNone, isNone
from utils.DbUtil import DatabaseUtil

import logging

logger = logging.getLogger('log')

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()


@method_decorator(csrf_exempt, name='dispatch')
def uploadJobFile(request):
    """
    脚本上传，上传的格式是.zip或者.jmx
    :param request:
    :return:
    """
    if request.method == 'POST':
        job_name = request.POST.get('job_name')
        description = request.POST.get('description')
        file = request.FILES.get('file', None)
        file_name = file.name
        # 文件存储
        if not file:
            responseData = success.success_response(msg='没有检测到上传文件，请重新上传')
            return JsonResponse(data=responseData, safe=False)
        else:
            timeNow = str(time.strftime("%Y%m%d%H%M%S"))
            save_file_name = timeNow + '_' + file.name
            f = open(os.path.join(settings.job_path, file.name), 'wb+')
            for chunk in file.chunks():
                f.write(chunk)
            f.close()
            try:
                # 将上传得文件进行重命名操作
                os.rename(settings.job_path + '\\' + file_name, settings.job_path + '\\' + save_file_name)
            except Exception as e:
                logger.error('重命名文件异常:{}'.format(e))
                responseData = error.error_response(msg='重命名文件异常')
                return JsonResponse(data=responseData, safe=False)
            job = Jobs(job_name=job_name, description=description, file_name=file_name, save_file_name=save_file_name)
            job.save()
            responseData = success.success_response(msg='上传文件成功')
            return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
def downloadJobFile(request):
    if request.method == 'GET':
        job_id = request.GET['job_id']
        file_name = Jobs.objects.get(job_id=job_id).save_file_name
        file_name = os.path.join(settings.job_path, file_name)
        file = open(file_name, 'rb')
        return FileResponse(file)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def searchJobFile(request):
    """
    搜索脚本
    :param request:
    :return:
    """
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        job_name = requestData.get('job_name')
        _data = Jobs.objects.filter(Q(job_name__icontains=job_name)).order_by('-create_time')
        _data = pageUtil.searchSqlFieldData(_data)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def deleteJobFile(request):
    """
    删除脚本
    :param request:
    :return:
    """
    if request.method == 'GET':
        job_id = request.GET['job_id']
        Jobs.objects.filter(job_id=job_id).update(is_delete='1')
        data = success.success_response(msg='删除脚本成功')
        return JsonResponse(data=data, safe=False)
