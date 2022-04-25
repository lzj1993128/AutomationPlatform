import os
import time

from AutomationPlatformDjango import settings

from common.base.BaseService import BaseService
from utils.MSLogUtil import MSLogUtil
from api.models import MSLog, Report
from utils.PageUtil import PageUtil

import logging

logger = logging.getLogger('log')


class MSLogService(BaseService):
    def __init__(self, msLogList, repord_id, case_id, case_name):
        self.case_id = case_id
        self.case_name = case_name
        self.repord_id = repord_id
        self.mslogUtil = MSLogUtil()
        self.pageUtil = PageUtil()
        self.mslogList = msLogList
        pass

    def getMSLogs(self):
        """
        链接服务器，抓取模块对应的日志
        :return:
        """
        try:
            mslogTimeNow = str(time.strftime("%Y%m%d%H"))
            report_name = Report.objects.get(report_id=self.repord_id).report_name
            mslogPath = os.path.join(settings.mslog_path, mslogTimeNow, report_name, str(self.case_id))
            logger.info('微服务错误用例抓取保存路劲创建成功{}'.format(mslogPath))
            if not os.path.exists(mslogPath): os.makedirs(mslogPath, mode=777)
            if len(self.mslogList) != 0:
                for mslog in self.mslogList:
                    ip = mslog.get('ms_ip')
                    port = mslog.get('ms_port')
                    user = mslog.get('ms_user')
                    password = mslog.get('ms_password')
                    log_path = eval(mslog.get('ms_log_list'))
                    for logs in log_path:
                        ms_name = logs.get('ms_name')
                        path = logs.get('ms_path')
                        mslogText = self.mslogUtil.connectMS(ip, port, user, password, path)
                        fileName = ms_name + '.log'
                        filePath = os.path.join(mslogPath, fileName)
                        with open(filePath, 'wb+') as f:
                            f.write(mslogText)
                zipOutName = str(self.case_id) + '.zip'
                zipOutPath = os.path.join(mslogPath, zipOutName)
                self.zipDir(mslogPath, zipOutPath)
                return zipOutName, zipOutPath
            else:
                logger.info('未获取到需要抓取的微服务日志')
        except Exception as e:
            logger.info('抓取微服务日志异常{}'.format(e))
            return None, None


    def runCatchMSLog(self):
        result = self.getMSLogs()
        logger.info('抓取日志成功')
        return result
