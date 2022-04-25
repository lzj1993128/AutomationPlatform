# -*- coding: utf-8 -*-
import logging
from datetime import datetime

import requests
import urllib3

from common.http.HttpError import HttpError

urllib3.disable_warnings()

logger = logging.getLogger('log')


class RunMethod:
    def check_http_is_success(self, res, requestDiff=None, compareTimeResult=True):
        """
        主要加上一层错误判断
        :param res:
        :param requestDiff: 请求差值
        :return:
        """
        error = HttpError()
        result_code = None
        result_json = res.json()
        if compareTimeResult:
            if res.status_code != 200:
                result_code = error.error_status('error_code_01', result_json, requestDiff)
            else:
                res_text = res.text
                if res_text is None:
                    result_code = error.error_status('error_code_02', result_json, requestDiff)
                elif 'error' in res_text:
                    result_code = error.error_status('error_code_03', result_json, requestDiff)
                elif 'error_code' in res_text:
                    result_code = error.error_status('error_code_03', result_json, requestDiff)
                elif '"success":false' in res_text:
                    result_code = error.error_status('error_code_04', result_json, requestDiff)
                else:
                    result_code = error.error_status('http_pass', result_json, requestDiff)
        else:
            result_code = error.error_status('error_code_06', result_json, requestDiff)
        return result_code

    def post_main(self, url, data=None, headers=None, json=None, takeUpTime=None):
        '''
        post方法
        :param url:
        :param data:
        :param header:
        :return:
        '''
        res = None
        requestBefore = datetime.now()
        res = requests.post(url=url, headers=headers, data=data, json=json, verify=False)
        if takeUpTime:
            requestAfter = datetime.now()
            requestDiff = (requestAfter - requestBefore).microseconds
            requestDiff = requestDiff / 1000000
            compareTimeResult = True if requestDiff < takeUpTime else False
            res_is_pass = self.check_http_is_success(res, requestDiff, compareTimeResult)
        else:
            res_is_pass = self.check_http_is_success(res)
        code = res_is_pass.get('code')
        acTakeUpTime = res_is_pass.get('acTakeUpTime')
        if code == 6:
            try:
                res = res.json()
                res_is_pass['acTakeUpTime'] = acTakeUpTime
                res_is_pass['result'] = res
                return res_is_pass
            except Exception as e:
                logger.error('序列化异常')
        else:
            return res_is_pass

    def get_main(self, url, params=None, headers=None, json=None, takeUpTime=None):
        """
         get方法
        :param url:
        :param data:
        :param header:
        :return:
        """
        res = None
        requestBefore = datetime.now()
        res = requests.get(url=url, params=params, headers=headers, json=json, verify=False)
        if takeUpTime:
            requestAfter = datetime.now()
            requestDiff = (requestAfter - requestBefore).microseconds
            requestDiff = requestDiff/1000000
            compareTimeResult = True if requestDiff < takeUpTime else False
            res_is_pass = self.check_http_is_success(res, requestDiff, compareTimeResult)
        else:
            res_is_pass = self.check_http_is_success(res)
        code = res_is_pass.get('code')
        acTakeUpTime = res_is_pass.get('acTakeUpTime')
        if code == 6:
            try:
                res = res.json()
                res_is_pass['acTakeUpTime'] = acTakeUpTime
                res_is_pass['result'] = res
                return res_is_pass
            except Exception as e:
                logger.error('序列化异常')
        else:
            return res_is_pass
