import logging
import re

from pymongo import MongoClient

logger = logging.getLogger('log')


class MongoDbUtil:
    def __init__(self, host, port):
        self.client = MongoClient(host, port)
        self.db = self.client["mydb"]

    # 表名
    def getVocde(self, phone, collection_name='sms_status'):
        """
        根据手机号查找验证码
        :param collection_name:
        :param phone:
        :return:
        """
        try:
            logger.info('通过mongo查找验证码')
            mycol = self.db[collection_name]
            phone = {"mobile": phone}
            times = [("createTime", -1)]
            result = list(mycol.find(phone).sort(times).limit(1))[0]
            vcode = result.get('content')
            vcode = re.findall('\d{6}', vcode)[0]
            return vcode
        except Exception as e:
            logger.error('mongo数据库获取验证码异常{}'.format(e))
            return None

    def getToolCode(self):
        mycol = self.db['sms_status']
        times = [("createTime", -1)]
        result = list(mycol.find().sort(times).limit(10))
        return result
