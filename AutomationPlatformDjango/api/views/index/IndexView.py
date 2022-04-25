import logging

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from Decorator.RequestDecorator import requestIntercept
from api.models import Project, Plan
from api.sqls.case.CaseViewSql import *
from api.sqls.index.IndexSql import *
from api.sqls.interface.InterfaceViewSql import *
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
def indexData(request):
    if request.method == 'GET':
        prjCount = Project.objects.filter(is_delete='0').count()
        caseCount = dbUtil.sqlResult(sql2())
        apiCount = len(dbUtil.sql_to_dict(InterfaceSql1('', '', '', '', '', '')))
        planCount = Plan.objects.filter(is_delete='0').count()
        responseData = success.success_response(msg='获取数据成功')
        responseData['data'] = {
            'prjCount': prjCount,
            'caseCount': caseCount,
            'apiCount': apiCount,
            'planCount': planCount
        }
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def indexStatistics(request):
    if request.method == 'GET':
        _data = dbUtil.sql_to_dict(sql3())
        _data = pageUtil.searchSqlFieldData(_data)
        responseData = success.success_response()
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def totalData(request):
    if request.method == 'GET':
        project_id = request.GET['project_id']
        planNums = dbUtil.sqlResult(IndexSql3(project_id))
        planRunTimes = dbUtil.sqlResult(IndexSql3(project_id))
        apiStatistics = dbUtil.sql_to_dict(IndexSql1(project_id))
        caseStatistics = dbUtil.sql_to_dict(IndexSql2(project_id))
        _data = {
            'planNums': planNums,
            'planRunTimes': planRunTimes,
            'apiStatistics': apiStatistics,
            'caseStatistics': caseStatistics
        }
        responseData = success.success_response()
        responseData['data'] = _data
        return JsonResponse(data=responseData, safe=False)
