import logging
import time

import redis

logger = logging.getLogger('log')


class RedisUtil:
    def __init__(self, host, port):
        self.r = self.connect_redis(host, port)

    def connect_redis(self, host, port, db=2):
        try:
            logger.info('链接redis')
            r = redis.Redis(host=host, port=port, decode_responses=True, db=db)
        except Exception as e:
            logger.error('连接redis出错，出错信息为：%s，隔3秒，尝试一次重新连接' % e)
            time.sleep(3)
            r = redis.Redis(host=host, port=port, decode_responses=True, db=db)
        return r

    # 获取用户短信验证码
    def get_vcode(self, phone):
        try:
            logger.info('进入redis，获取验证码')
            result = self.r.get("vcode:login:sms:%s" % phone)
            result = result[1:7]
            return result
        except Exception as e:
            logger.error('获取验证码异常{}'.format(e))

    # 获取用户token值
    def get_token(self, memberId):
        token = self.r.get("member:info:token:%s" % memberId)
        return token
