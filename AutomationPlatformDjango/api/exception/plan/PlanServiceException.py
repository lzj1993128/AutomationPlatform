import logging

logger = logging.getLogger('log')


class LackMustRequestParam(Exception):
    """
    缺少必填字段异常
    """

    def __init__(self, errorInfo):
        self.errorInfo = errorInfo

    def __str__(self):
        msg = str(self.errorInfo)
        return msg