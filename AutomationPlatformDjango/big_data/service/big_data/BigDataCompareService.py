import re
import json

from django.contrib.auth.hashers import make_password, check_password

from common.base.BaseService import BaseService
from api.models import Database
from big_data.models import BigData
from utils.Dubbo import Dubbo, GetDubboService
from big_data.service.big_data.BigDataExcelSavaService import BigDataExcelSaveService
from big_data.service.big_data.HandleDubboResultService import HandleDubboResultService
from big_data.service.big_data.HandleHttpsRequestService import HandleHttpsResultService
from big_data.service.big_data.HandleSqlResultService import HandlerSqlResultService

import logging

logger = logging.getLogger('log')


class BigDataComepareService(BaseService):
    def __init__(self, big_data_id, envList, dbList=None, report_id=None):
        self.big_data_id = big_data_id
        self.envList = envList
        if dbList is not None:
            if isinstance(dbList, str):
                self.dbList = eval(dbList)
            else:
                self.dbList = dbList
        else:
            self.dbList = dbList
        self.report = report_id
        print(self.report)
        pass

    def getDubboZK(self):
        """
        获取dubbo zk注册服务器
        :return:
        """
        api_database = BigData.objects.get(big_data_id=self.big_data_id).api_database
        return api_database

    def getApiName(self):
        """
        获取dubbo接口服务名字
        :return:
        """
        api_name = BigData.objects.get(big_data_id=self.big_data_id).api_name
        return api_name

    def getApiMethod(self):
        """
        获取dubbo接口服务方法名
        :return:
        """
        api_method = BigData.objects.get(big_data_id=self.big_data_id).api_method
        return api_method

    def getDubboJson(self):
        """
        获取dubbo json参数
        :return:
        """
        requestJson = BigData.objects.get(big_data_id=self.big_data_id).requestJson
        requestJson = re.sub('\s+', '', requestJson).strip()
        requestJson = json.loads(requestJson)
        return requestJson

    def getReponseField(self):
        """
        获得接口返回有数据的那个key
        :return:
        """
        reponse_field = BigData.objects.get(big_data_id=self.big_data_id).reponse_field
        return reponse_field

    def doDubboConnect(self):
        """
        处理dubbo连接
        :return:
        """
        logger.info("通过zk注册中心，获取dubbo服务器部署信息")
        api_database = self.getDubboZK()
        apiName = self.getApiName()
        apiMethod = self.getApiMethod()
        requestJson = self.getDubboJson()
        getDubboService = GetDubboService(api_database)
        dubboService = getDubboService.getDubboInfo(apiName)
        host = dubboService.get("server_host")
        port = dubboService.get("server_port")
        dubbo = Dubbo(host, port)
        result = dubbo.invokeCommand(apiName, apiMethod, requestJson)
        logger.info(result)
        reponse_field = self.getReponseField()
        handleDubboResultService = HandleDubboResultService(result, reponse_field)
        result = handleDubboResultService.handleDubboResult()
        return result

    def doHttpsConnect(self):
        """
        处理http请求
        :return:
        """
        api_url = BigData.objects.get(big_data_id=self.big_data_id).api_url
        method = BigData.objects.get(big_data_id=self.big_data_id).method
        data_type = BigData.objects.get(big_data_id=self.big_data_id).data_type
        api_name = BigData.objects.get(big_data_id=self.big_data_id).api_name
        requestHeader = json.loads(
            re.sub('\s+', '', BigData.objects.get(big_data_id=self.big_data_id).requestHeader).strip())
        requestBody = json.loads(
            re.sub('\s+', '', BigData.objects.get(big_data_id=self.big_data_id).requestBody).strip())
        reponse_field = BigData.objects.get(big_data_id=self.big_data_id).reponse_field
        project_id = BigData.objects.get(big_data_id=self.big_data_id).project_id
        handHttp = HandleHttpsResultService(requestHeader, requestBody, project_id, envData=self.envList)
        needHandleResult = handHttp.getNeedHandleResult(api_url, method, data_type, reponse_field)
        return needHandleResult

    def getProjectId(self):
        """
        获取大数据所属项目
        :return:
        """
        project_id = BigData.objects.get(big_data_id=self.big_data_id).project_id
        return project_id

    def getDataBase(self):
        """
        获取需要查询的报表数据库
        :return:
        """
        print(self.dbList)
        if self.dbList is None or len(self.dbList) == 0:
            print('获取数据库id')
            db_id = BigData.objects.get(big_data_id=self.big_data_id).db_id
            print(db_id)
            return db_id
        else:
            print('else逻辑')
            bigDataBelongProject = self.getProjectId()
            print(bigDataBelongProject)
            for db in self.dbList:
                print(db)
                selectDbProject = db.get('selectDbProject')
                print(selectDbProject)
                selectDb = db.get('selectDb')
                if bigDataBelongProject == selectDbProject:
                    db_id = selectDb
                    return db_id

    def getSql(self):
        """
        获取数据库语句
        :return:
        """
        sql = BigData.objects.get(big_data_id=self.big_data_id).sql
        logger.info('sql:', sql)
        return sql

    def doDatabase(self):
        """
        处理数据库
        :return:
        """
        db_id = self.getDataBase()
        db_name = Database.objects.get(db_id=db_id).db_name
        db_host = Database.objects.get(db_id=db_id).db_host
        db_port = int(Database.objects.get(db_id=db_id).db_port)
        db_user = Database.objects.get(db_id=db_id).db_user
        db_passwd = Database.objects.get(db_id=db_id).db_passwd
        sql = self.getSql()
        logger.info(sql, db_name, db_host, db_user, db_passwd, db_port)
        result = self.executeSql(sql, db_name, db_host, db_user, db_passwd, db_port)
        logger.info(result)
        handlerSqlResultService = HandlerSqlResultService(list(result))
        result = handlerSqlResultService.handleSqlResult()
        return result

    def getTargetList(self):
        """
        获得指标字段
        :return:
        """
        requestCompareFieldList = eval(BigData.objects.get(big_data_id=self.big_data_id).requestCompareFieldList)
        return requestCompareFieldList

    def getHttpOrDubbo(self):
        """
        获取请求方式,http或者dubbo
        :return:
        """
        request_method = BigData.objects.get(big_data_id=self.big_data_id).request_method
        return request_method

    def doRequestCompareFieldList(self):
        """
        对指标进行操作
        获取接口返回得数
        获取数据库请求返回得数
        RESULT_CHOICE = ((0, '未运行'), (1, '运行中'), (2, '运行结束'), (3, '运行异常'))
        :return:
        """
        try:
            BigData.objects.filter(big_data_id=self.big_data_id).update(run_status='1')
            requestCompareFieldList = self.getTargetList()
            databaseResult = self.doDatabase()
            request_method = self.getHttpOrDubbo()
            apiRequest = self.doHttpsConnect() if request_method == 'http' else self.doDubboConnect()
            bigDataExcelSaveService = BigDataExcelSaveService(self.big_data_id, requestCompareFieldList, apiRequest,
                                                              databaseResult, self.report)
            bigDataExcelSaveService.handleRequestCompareFieldList()
            BigData.objects.filter(big_data_id=self.big_data_id).update(run_status='2')
        except Exception as e:
            logger.info('比对数据异常，异常信息：{}'.format(e))
            BigData.objects.filter(big_data_id=self.big_data_id).update(run_status='3')
