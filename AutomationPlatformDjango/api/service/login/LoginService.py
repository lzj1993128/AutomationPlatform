from common.base.BaseService import BaseService
from api.models import User

import logging

logger = logging.getLogger('log')


class LoginService(BaseService):
    def __init__(self, ip, username):
        self.ip = ip
        self.username = username

    def checkLoginIP(self):
        """
        确认ip，如果是同一个IP，则不计入访问次数
        :return:
        """
        try:
            dataIP = User.objects.get(username=self.username).last_login_ip
            logger.info('获取的ip'.format(self.ip))
            logger.info(dataIP)
            login_count = User.objects.get(username=self.username).login_count
            if dataIP != self.ip:
                logger.info('检测到登录ip不一致，添加次数')
                login_count = login_count + 1
                User.objects.filter(username=self.username).update(login_count=login_count)
            else:
                logger.info('登录ip一致，不进行统计')
        except Exception as e:
            logger.error('统计登录次数异常')
            login_count = User.objects.get(username=self.username).login_count
            User.objects.filter(username=self.username).update(login_count=login_count + 1)
