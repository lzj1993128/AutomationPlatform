import os

from django.db.models import Q
from api.models import Report, CaseTestResult
from wsgiref.util import FileWrapper
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from Decorator.RequestDecorator import requestIntercept
from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from utils.PageUtil import PageUtil
from common.base.baseClass import getBodyData
from utils.DbUtil import DatabaseUtil
from api.service.report.ReportService import ReportService

success = SuccessResponse()
error = ErrorResponse()
pageUtil = PageUtil()
dbUtil = DatabaseUtil()


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def searchReport(request):
    """
    get请求取最新的10次报告（形成柱状图）以及这个报告的数据（不包括执行用例的数据）；
    post请求取单个报告的数据（形成饼图），以及这个报告的执行用例的数据
    :param request:
    :return:
    """
    if request.method == 'GET':
        plan_id = request.GET['plan_id']
        _data = Report.objects.filter(plan_id=plan_id).order_by('-create_time')[0:9]
        _data = pageUtil.searchSqlFieldData(_data)
        # 柱状图
        reportService = ReportService()
        histogram = reportService.handleHistogram(_data)
        responseData = success.success_response()
        responseData["data"] = _data
        responseData["histogram"] = histogram
        return JsonResponse(data=responseData, safe=False)

    if request.method == 'POST':
        requestData = getBodyData(request.body)
        page = requestData.get('page')
        pageSize = requestData.get('pageSize')
        report_id = requestData.get('report_id')
        # 饼图
        report_data = Report.objects.filter(report_id=report_id)
        report_data = pageUtil.searchSqlFieldData(report_data)
        reportService = ReportService()
        pieChart = reportService.handlePieChart(report_data)
        result = requestData.get('result')
        if result == '':
            _data = CaseTestResult.objects.filter(report_id__report_id__exact=report_id)
        else:
            _data = CaseTestResult.objects.filter(Q(report_id__report_id__exact=report_id) & Q(result=result))
        _data = pageUtil.searchSqlFieldData(_data)
        pageInfo = pageUtil.getPageInfo(_data, page, pageSize)
        _data = pageUtil.getDataInfo(_data, page, pageSize)
        responseData = success.success_response()
        responseData['data'] = _data
        responseData['pageInfo'] = pageInfo
        responseData['pieChart'] = pieChart
        return JsonResponse(data=responseData, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
@requestIntercept
def downLoadMSLog(request):
    """
    提供错误服务端日志下载功能
    :param request:
    :return:
    """
    if request.method == 'GET':
        case_result_id = request.GET['case_result_id']
        mslog = CaseTestResult.objects.get(case_result_id=case_result_id)
        mslog_name = mslog.mslog_name
        mslog_path = mslog.mslog_path
        wrapper = FileWrapper(open(mslog_path, 'rb'))
        response = StreamingHttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}'.format(mslog_name)
        response['Content-Length'] = os.path.getsize(mslog_path)
        return response
