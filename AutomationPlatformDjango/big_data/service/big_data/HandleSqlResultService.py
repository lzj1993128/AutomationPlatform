from common.base.BaseService import BaseService
from utils.PageUtil import PageUtil

pageUtil = PageUtil()


class HandlerSqlResultService(BaseService):
    def __init__(self, sqlResult):
        self.sqlResult = sqlResult

    def handleSqlResult(self):
        """
        处理数据库返回数据
        :return:
        """
        result = pageUtil.searchSqlFieldData(self.sqlResult)
        return result
