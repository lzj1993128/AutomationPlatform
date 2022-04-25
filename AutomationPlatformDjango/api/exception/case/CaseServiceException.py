import logging

logger = logging.getLogger('log')


class EvalError(Exception):
    """
    请求数据eval异常
    """

    def __init__(self, errorInfo):
        self.errorInfo = errorInfo

    def __str__(self):
        msg = str(self.errorInfo) + ':处理请求的数据eval异常,请检查请求数据是否符合格式'
        return msg


class RequestJsonError(Exception):
    def __init__(self, errorInfo):
        self.errorInfo = errorInfo

    def __str__(self):
        msg = str(self.errorInfo) + '请求json存在异常'
        return msg


class RequestBodyError(Exception):
    def __init__(self, errorInfo):
        self.errorInfo = errorInfo

    def __str__(self):
        msg = str(self.errorInfo) + '请求body存在异常'
        return msg



class ConnectSqlError(Exception):
    def __init__(self, errorInfo):
        self.errorInfo = errorInfo

    def __str__(self):
        msg = str(self.errorInfo) + '数据库异常'
        return msg