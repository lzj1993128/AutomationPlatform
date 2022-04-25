import time
import os
from big_data.models import BigData, BigDataHistory
from utils.ExcelUtil import ExcelUtil
from big_data.path import excel_path
from common.base.BaseService import BaseService

import logging

logger = logging.getLogger('log')


class BigDataExcelSaveService(BaseService):
    def __init__(self, big_data_id, requestCompareFieldList, apiResult, databaseResul, report_id=None):
        """
        初始化指标字段
        :param requestCompareFieldList:指标字段
        :param dubboResult:http接口或者dubbo返回得结果
        :param databaseResul:通过查询数据库得方式获得得结果
        """
        self.requestCompareFieldList = requestCompareFieldList
        self.apiResult = apiResult
        self.databaseResult = databaseResul
        self.big_data_id = big_data_id
        self.big_data_his_id = self.addBigDataHistory(report_id)
        self.excelPath = self.creatExcelPath()
        self.apiExcelPath = self.createApiExcel()
        self.apiExcelUtil = ExcelUtil(self.apiExcelPath, flag=True)
        self.compareExcelPath = self.createCompareExcel()
        self.compareExcelUtil = ExcelUtil(self.compareExcelPath, flag=True)

    def creatExcelPath(self):
        """
        创建一个存接口的excel
        :return:
        """
        nowTimeH = str(time.strftime("%Y%m%d%H"))
        nowTimeM = str(time.strftime("%Y%m%d%H%M"))
        excelPath = os.path.join(excel_path, nowTimeH, str(self.big_data_id), nowTimeM)
        if not os.path.exists(excelPath): os.makedirs(excelPath, mode=0o777)
        return excelPath

    def createApiExcel(self):
        """
        创建一个接口结果的excel文件
        :return:
        """
        now = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        excelName = 'apiResule' + '_' + now + '.xlsx'
        excelPath = os.path.join(self.excelPath, excelName)
        return excelPath

    def createCompareExcel(self):
        """
        创建一个比较结果的excel文件
        :return:
        """
        now = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        excelName = 'compareExcelResult' + '_' + now + '.xlsx'
        excelPath = os.path.join(self.excelPath, excelName)
        return excelPath

    def handleRequestCompareFieldList(self):
        """
        处理数据：[{'name': '销售额', 'api_field_name': 'sell', 'sql_field_name': 'sellee'}]
        处理指标字段
        :return:
        """
        nameList = []
        apiFieldNameList = []
        sqlFieldNameList = []
        for fieldList in self.requestCompareFieldList:
            name = fieldList.get('name')
            api_field_name = fieldList.get('api_field_name')
            sql_field_name = fieldList.get('sql_field_name')
            nameList.append(name)
            apiFieldNameList.append(api_field_name)
            sqlFieldNameList.append(sql_field_name)
        logger.info('指标列表nameList：{}'.format(nameList))
        logger.info('指标列表对应的接口字段列表apiFieldNameList：{}'.format(apiFieldNameList))
        logger.info('指标列表对应的数据库列表sqlFieldName：{}'.format(sqlFieldNameList))
        self.saveApiResultToExcel(nameList, apiFieldNameList)
        self.saveCompareResultToExcel(nameList, apiFieldNameList, sqlFieldNameList)
        self.statisticsApiExcelPass()
        self.statisticsCompareExcelPass()
        self.zipApiCsv()

    def saveApiResultToExcel(self, nameList, apiFieldNameList):
        """
        将接口结果保存到excel,并进行判断
        :return:
        """
        lenNameList = len(nameList)
        for nameIndex in range(lenNameList):
            # 将指标填入第一行和第二行
            self.apiExcelUtil.write_excel(0, nameList[nameIndex], nameIndex)
            self.apiExcelUtil.write_excel(1, apiFieldNameList[nameIndex], nameIndex)
        self.apiExcelUtil.write_excel(0, '错误原因', lenNameList)
        self.apiExcelUtil.write_excel(0, '结果', lenNameList + 1)
        if len(self.apiResult) == 0:
            self.apiExcelUtil.write_excel(1, '接口返回数据为空', lenNameList)
            self.apiExcelUtil.write_excel(1, 'fail', lenNameList + 1)
            return None
        row = 2
        for result in self.apiResult:
            self.apiExcelUtil.write_excel(row, '', lenNameList)
            self.apiExcelUtil.write_excel(row, 'pass', lenNameList + 1)
            # 查出每个结果的keys（），和存入数据的keys数量做比较,如果相同的数量一致，说明返回的数据不正确
            resultKeys = result.keys()
            duplicateFields = [x for x in resultKeys if x in apiFieldNameList]
            logger.info('打印出公共的字段：{}'.format(duplicateFields))
            for target in result.keys():
                if target in apiFieldNameList and len(duplicateFields) == len(apiFieldNameList):
                    # 如果字段在指标字段里面并且共有字段相同，则这个字段通过，反之则不通过
                    self.apiExcelUtil.write_excel(row, result[target], apiFieldNameList.index(target))
                else:
                    self.apiExcelUtil.write_excel(row, '参数缺失:' + target, lenNameList)
                    self.apiExcelUtil.write_excel(row, 'fail', lenNameList + 1)
                    continue
            if row < len(self.apiResult) + 2:
                row += 1
            else:
                break

    def saveCompareResultToExcel(self, nameList, apiFieldNameList, sqlFieldNameList):
        """
        将接口和数据库查询出来的数据存放到excel中
        :return:
        """
        lenNameList = len(nameList)
        for nameIndex in range(lenNameList):
            self.compareExcelUtil.write_excel(0, '接口' + nameList[nameIndex], nameIndex)
            self.compareExcelUtil.write_excel(1, apiFieldNameList[nameIndex], nameIndex)
            self.compareExcelUtil.write_excel(0, 'sql' + nameList[nameIndex], lenNameList + nameIndex)
            self.compareExcelUtil.write_excel(1, sqlFieldNameList[nameIndex], lenNameList + nameIndex)
        self.compareExcelUtil.write_excel(0, '错误原因', lenNameList * 2)
        self.compareExcelUtil.write_excel(0, '结果', lenNameList * 2 + 1)
        lenApiResult = len(self.apiResult)
        lenDatabaseResult = len(self.databaseResult)
        if lenApiResult != lenDatabaseResult:
            logger.info('接口查询结果:{}与数据库查询结果:{}数量不一致'.format(str(lenApiResult), str(lenDatabaseResult)))
            self.compareExcelUtil.write_excel(0, '接口查询结果:{}与数据库查询结果:{}数量不一致'.format(lenApiResult, lenDatabaseResult),
                                              lenNameList * 2)
            self.compareExcelUtil.write_excel(0, 'fail', lenNameList * 2 + 1)
            return None
        if lenApiResult == lenDatabaseResult:
            logger.info('两边查询结果数量一致')
            # 将接口返回的数据填入表格
            row = 2
            for result in self.apiResult:
                for target in result.keys():
                    if target in apiFieldNameList:
                        self.compareExcelUtil.write_excel(row, result[target], apiFieldNameList.index(target))
                if row < lenApiResult + 2:
                    row += 1
                else:
                    break
            #   将数据库已清洗过的数据填入表格
            row = 2
            for result in self.databaseResult:
                for target in result.keys():
                    if target in sqlFieldNameList:
                        self.compareExcelUtil.write_excel(row, result[target],
                                                          sqlFieldNameList.index(target) + lenNameList)
                if row < lenDatabaseResult + 2:
                    row += 1
                else:
                    break
            # 这里写比对逻辑
            for row in range(lenApiResult):
                row = row + 2
                for col in range(lenNameList):
                    print('列', col)
                    print(
                        '接口值{}以及类型{}'.format(self.compareExcelUtil.getCellValue(row, col),
                                             type(self.compareExcelUtil.getCellValue(row, col))))
                    print('列', col + lenNameList)
                    print('数据库值{}和类型{}'.format(self.compareExcelUtil.getCellValue(row, col + lenApiResult),
                                               type(self.compareExcelUtil.getCellValue(row, col + lenNameList))))
                    if self.compareExcelUtil.getCellValue(row, col) == self.compareExcelUtil.getCellValue(row,
                                                                                                          col + lenNameList):
                        print('一致')
                        self.compareExcelUtil.write_excel(row, 'pass', lenNameList * 2 + 1)
                    else:
                        print('不一致')
                        self.compareExcelUtil.write_excel(row, '参数数值不一致', lenNameList * 2)
                        self.compareExcelUtil.write_excel(row, 'fail', lenNameList * 2 + 1)
                        continue

    def statisticsApiExcelPass(self):
        """
        统计接口因返回的字段数
        :return:
        """
        excelUtil = ExcelUtil(self.apiExcelPath)
        rows = excelUtil.getRows() - 2
        cols = excelUtil.getCols()
        colData = excelUtil.getColsValues(cols - 1)
        passNum = colData.count('pass')
        failNum = colData.count('fail')
        errorNUm = colData.count('error')
        if int(rows) != 0:
            passPercent = int(passNum) / int(rows)
        else:
            passPercent = 0
        BigDataHistory.objects.filter(big_data_his_id=self.big_data_his_id).update(total_api_nums=rows,
                                                                                   pass_api_pers=passPercent,
                                                                                   pass_api_nums=passNum,
                                                                                   fail_api_nums=failNum,
                                                                                   error_api_nums=errorNUm)

    def statisticsCompareExcelPass(self):
        """
        统计接口因返回的字段数
        :return:
        """
        excelUtil = ExcelUtil(self.compareExcelPath)
        rows = excelUtil.getRows() - 2
        cols = excelUtil.getCols()
        colData = excelUtil.getColsValues(cols - 1)
        passNum = colData.count('pass')
        failNum = colData.count('fail')
        errorNUm = colData.count('error')
        if int(rows) != 0:
            passPercent = int(passNum) / int(rows)
        else:
            passPercent = 0
        BigDataHistory.objects.filter(big_data_his_id=self.big_data_his_id).update(total_compare_nums=rows,
                                                                                   pass_compare_pers=passPercent,
                                                                                   pass_compare_nums=passNum,
                                                                                   fail_compare_nums=failNum,
                                                                                   error_compare_nums=errorNUm)

    def zipApiCsv(self):
        """
        将结果保存成zip
        :return:
        """
        now = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        zipOutName = '执行结果' + '_' + now + '.zip'
        zipOutPath = os.path.join(self.excelPath, zipOutName)
        self.zipDir(self.excelPath, zipOutPath)
        BigDataHistory.objects.filter(big_data_his_id=self.big_data_his_id).update(csv_file_name=zipOutName,
                                                                                   csv_file_path=self.excelPath)

    def addBigDataHistory(self, report_id):
        """
        增加一个大数据历史报告
        :return:
        """
        now = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        big_data_his_name = '大数据比对结果' + '_' + str(now)
        print(666666)
        bigDataHistory = BigDataHistory(big_data_id=self.big_data_id, big_data_his_name=big_data_his_name,
                                        report=report_id)
        bigDataHistory.save()
        big_data_his_id = bigDataHistory.big_data_his_id
        return big_data_his_id
