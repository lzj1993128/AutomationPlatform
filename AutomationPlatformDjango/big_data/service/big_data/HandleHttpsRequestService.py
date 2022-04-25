import json

from common.base.BaseService import BaseService
from utils.SignUtil import signByMd5
from api.models import Env

import logging

logger = logging.getLogger('log')


class HandleHttpsResultService(BaseService):
    def __init__(self, requestHeader, requestBody, project_id, envData=None):
        self.requestHeader = requestHeader
        self.requestBody = requestBody
        if envData is not None:
            if isinstance(envData, str):
                self.envData = eval(envData)
            else:
                self.envData = envData
        self.project_id = project_id

    def handleRequest(self):
        """
        先对请求header和请求body进行处理,获得签名后，返回一个处理好的body
        :return:
        """
        url = 'https://test-i0-superapiplus.carzone360.com/superapi/ps/getH5SessionAndSecret'
        result = self.requestApi('get', url)
        secret = self.get_target_value('secret', result, [])[0]
        sessionId = self.get_target_value('session-id', result, [])[0]
        if 'session-id' in self.requestHeader.keys():
            self.requestHeader['session-id'] = sessionId
        if 'timestamp' in self.requestBody.keys():
            self.requestBody['timestamp'] = self.get_now()
        sign = signByMd5(self.requestHeader, self.requestBody, secret)
        self.requestBody['sign'] = sign
        print(self.requestBody['data'])
        print('sign', sign)

    def getEnvUrl(self, project_id):
        """
        返回各个接口所需要的环境地址，根据项目id判断
        :param project_id: 传进一个接口储存的项目id参数
        :return: 项目url
        """
        try:
            url = ''
            for env in self.envData:
                prj_id = env.get('selectEvnPrject')
                other_url = env.get('other_url')
                if project_id == prj_id:
                    if other_url == '':
                        env_id = int(env.get('selectEvnUrl'))
                        url = Env.objects.get(env_id=env_id).env_url
                    else:
                        url = other_url
            logger.info('请求的url地址为:{}'.format(url))
            return url
        except Exception as e:
            logger.error(e)

    def getNeedHandleResult(self, api_url, method, data_type, reponse_field):
        """
        返回一个需要处理的结果
        :param api_url:
        :param method:
        :param data_type:
        :param reponse_field:
        :return:
        """
        self.handleRequest()
        url = self.getEnvUrl(self.project_id) + api_url
        result = self.requestApi(method=method, url=url, headers=self.requestHeader, data=self.requestBody,
                                 data_type=data_type)
        needHandleResult = self.get_target_value(reponse_field, result, [])[0]
        needHandleResult = self.handleData(needHandleResult)
        print('打印needhandleresult：', needHandleResult)
        return needHandleResult

    def handleData(self, needHandleResult):
        """
        将接口返回的结果日期20/03进行特殊处理
        :param result:
        :return:
        """
        for result in needHandleResult:
            if 'saleMonth' in result.keys() or 'saleData' in result.keys():
                if '/' in result['saleMonth']:
                    data = result['saleMonth'].split('/')
                    year = data[0] + '20'
                    month = data[1]
                    newData = year + '-' +month
                    result['saleMonth'] = newData
                elif '/' in result['saleData']:
                    data = result['saleData'].split('/')
                    year = data[0] + '20'
                    month = data[1]
                    newData = year + '-' +month
                    result['saleData'] = newData
        return needHandleResult
