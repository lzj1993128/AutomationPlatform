import json
import logging
import re

from big_data.exception.big_data.BigDataRequestException import RequestException
from common.base.BaseService import BaseService
from utils.Dubbo import Dubbo, GetDubboService
from utils.SignUtil import signByMd5
from common.big_data.BigDataCommon import BigDataCommon

logger = logging.getLogger('log')


class TestRunRequest(BaseService):
    def __init__(self, requestInfo):
        self.requestInfo = requestInfo

    def dubboTestRun(self):
        """
        测试dubbo运行
        :param zk_database: zk地址
        :param apiName: 服务名
        :param apiMethod: 服务方法名
        :param requestJson: 传递的参数
        :return:
        """
        try:
            logger.info('dubbo接口测试')
            dubboRequestInfo = self.requestInfo.get('dubboRequest')
            zk_database = dubboRequestInfo.get('zk_database')
            apiMethod = dubboRequestInfo.get('zk_api_method')
            apiName = dubboRequestInfo.get('zk_api_name')
            requestDubboList = dubboRequestInfo.get('request_json_list')
            requestDubboListStr = self.handleDubboRequestList(requestDubboList)
            getDubboService = GetDubboService(zk_database)
            dubboService = getDubboService.getDubboInfo(apiName)
            host = dubboService.get('server_host')
            port = dubboService.get('server_port')
            dubbo = Dubbo(host, port)
            result = dubbo.invokeCommand(apiName, apiMethod, requestDubboListStr)
            logger.info('打印dubbo请求的结果：{}'.format(result))
            return result
        except Exception as e:
            logger.error('打印请求dubbo请求异常：{}'.format(e))
            raise RequestException('请求dubbo异常：{}'.format(e))


    def httpTestRun(self):
        """
        http请求
        :return:
        """
        try:
            logger.info('http接口测试')
            httpRequestInfo = self.requestInfo.get('httpRequest')
            project_id = self.requestInfo.get('project_id')
            apiUrl = httpRequestInfo.get('api_url')
            method = httpRequestInfo.get('method')
            data_type = httpRequestInfo.get('data_type')
            requestHeader = json.loads(re.sub('\s+', '', httpRequestInfo.get('requestHeader')).strip())
            requestBody = json.loads(re.sub('\s+', '', httpRequestInfo.get('requestBody')).strip())
            # 解决网关签名问题
            url = 'https://test-i0-superapiplus.carzone360.com/superapi/ps/getH5SessionAndSecret'
            result = self.requestApi('get', url)
            secret = self.get_target_value('secret', result, [])[0]
            sessionId = self.get_target_value('session-id', result, [])[0]
            if 'session-id' in requestHeader.keys():
                requestHeader['session-id'] = sessionId
            if 'timestamp' in requestBody.keys():
                requestBody['timestamp'] = self.get_now()
            if 'ac-session-id' in requestHeader.keys():
                bigDataCommon = BigDataCommon()
                acSessionId = bigDataCommon.handleRequestDubboHeaders()
                requestHeader['ac-session-id'] = acSessionId
            sign = signByMd5(requestHeader, requestBody, secret)
            requestBody['sign'] = sign
            envListData = self.requestInfo.get('envForm')
            url = self.envUrl(project_id, envListData) + apiUrl
            result = self.requestApi(method, url, headers=requestHeader, data=requestBody, data_type=data_type)
            return result
        except Exception as e:
            logger.error('打印请求http请求异常：{}'.format(e))
            raise RequestException('请求http异常：{}'.format(e))

    def runTest(self):
        """
        总的运行入口
        :return:
        """
        request_method = self.requestInfo.get('request_method')
        try:
            result = self.dubboTestRun() if request_method == 'dubbo' else self.httpTestRun()
            return result
        except RequestException:
            errorInfo = '接口请求错误，错误信息:{}'.format(RequestException)
            raise RequestException(errorInfo)
