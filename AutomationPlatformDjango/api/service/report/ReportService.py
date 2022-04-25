from common.base.BaseService import BaseService
from utils.ReportUtil import ReportUtil
from utils.PageUtil import PageUtil

from api.models import CaseTestResult

import logging

logger = logging.getLogger('log')


class ReportService(BaseService):
    def __init__(self):
        self.reportUtil = ReportUtil()
        self.pageUtil = PageUtil()

    def handleHistogram(self, data):
        """
        处理成柱状图
        :param data:
        :return:
        """
        rows = []
        columns = ['次数', '通过数', '失败数', '错误数']
        for i in range(len(data)):
            rowDict = dict.fromkeys(columns)
            index = i + 1
            pass_num = data[i]['pass_num']
            fail_num = data[i]['fail_num']
            error_num = data[i]['error_num']
            rowDict['次数'] = index
            rowDict['通过数'] = pass_num
            rowDict['失败数'] = fail_num
            rowDict['错误数'] = error_num
            rows.append(rowDict)
        histogram = {'columns': columns, 'rows': rows}
        return histogram

    def handlePieChart(self, data):
        """
        处理成饼图
        :param data:
        :return:
        """
        columns = ['类型', '数量']
        rows = []
        pass_num = data[0].get('pass_num')
        fail_num = data[0].get('fail_num')
        error_num = data[0].get('error_num')
        num = [pass_num, fail_num, error_num]
        for i in range(len(num)):
            rowDict = dict.fromkeys(columns)
            if i == 0:
                rowDict['类型'] = '通过数'
            elif i == 1:
                rowDict['类型'] = '失败数'
            else:
                rowDict['类型'] = '错误数'
            rowDict['数量'] = num[i]
            rows.append(rowDict)
        pieChart = {'columns': columns, 'rows': rows}
        return pieChart

    def handleReport(self, data):
        """
        总的report数据
        :param data:
        :return: report
        """
        try:
            logger.info('打印出需要做成报告的邮件{}'.format(data))
            report_id = data.get('report_id')
            total_num = str(data.get('case_num'))
            pass_num = str(data.get('pass_num'))
            fail_num = str(data.get('fail_num'))
            error_num = str(data.get('error_num'))
            caseResultQuery = CaseTestResult.objects.filter(report_id=report_id)
            fields = ['case_id', 'case_name', 'result']
            caseResultList = self.pageUtil.searchSqlFieldData(result=caseResultQuery, fields=fields)
            trList = []
            for caseResult in caseResultList:
                case_id = caseResult.get('case_id')
                case_name = caseResult.get('case_name')
                result = caseResult.get('result')
                tr = self.reportUtil.trList(case_id, case_name, result)
                trList.append(tr)
            trListStr = ''.join(trList)
            report = self.reportUtil.report(title='自动化测试报告', totalNum=total_num, passNum=pass_num, failNum=fail_num,
                                            errorNum=error_num, trList=trListStr)
            return report
        except Exception as e:
            logger.error('组成报告html异常{}'.format(e))
