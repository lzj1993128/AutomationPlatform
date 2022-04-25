import logging

logger = logging.getLogger('log')


class RequestException(Exception):
    """
    请求异常
    """

    def __init__(self, errorInfo):
        self.errorInfo = errorInfo

    def __str__(self):
        msg = str(self.errorInfo)
        return msg
