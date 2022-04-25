import logging
import os
from wsgiref.util import FileWrapper

from django.http import JsonResponse, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from big_data.models import BigDataHistory
from big_data.sqls.big_data.BigDataHistorySql import *
from common.base.baseClass import getBodyData
from common.reponse.ErrorResponse import ErrorResponse
from common.reponse.SuccessResponse import SuccessResponse
from utils.DbUtil import DatabaseUtil
from utils.PageUtil import PageUtil

logger = logging.getLogger('log')

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def searchBigHistory(request):
    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        big_data_id_list = requestData.get('big_data_id_list')
        _data = dbUtil.sql_to_dict(bigDataHistorySql(big_data_id_list))
        _data = pageUtil.searchSqlFieldData(_data)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
def downloadBigDataHistory(request):
    """
    提供下载功能
    :param request:
    :return:
    """
    if request.method == 'GET':
        big_data_his_id = request.GET['big_data_his_id']
        bigDataHistory = BigDataHistory.objects.get(big_data_his_id=big_data_his_id)
        name = bigDataHistory.csv_file_name
        path = bigDataHistory.csv_file_path
        wrapper = FileWrapper(open(path, 'rb'))
        response = StreamingHttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}'.format(name)
        response['Content-Length'] = os.path.getsize(path)
        return response
