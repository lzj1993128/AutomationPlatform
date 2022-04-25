import datetime


class PageViewMiXin:
    def __init__(self, result=None, page=1, pageSize=10):
        self.page = page
        self.pageSize = pageSize
        self.result = result
        self.count = self.getTotalCount()
        self.pageTotal = self.getRequestPageTotal()

    def getTotalCount(self):
        """
        获取数据的总数
        :return:
        """
        count = self.result.count()
        return count

    def getRequestPageTotal(self):
        """
        获取前端传过来1页需要的数据
        :return:
        """
        pageTotal = self.page * self.pageSize
        return pageTotal

    def getPageInfo(self):
        """
        返回分页信息
        :param result:
        :param page:
        :param pageSize:
        :return:
        """
        pageInfo = dict()
        if self.count != 0:
            if self.count < self.pageTotal:
                pageInfo['pageMax'] = 1
            else:
                page = int(self.count / self.pageSize)
                pageMax = page + 1
                pageInfo['pageMax'] = pageMax
        pageInfo['page'] = self.page
        pageInfo['pageSize'] = self.pageSize
        pageInfo['pageToal'] = self.count
        return pageInfo

    def getDataInfo(self,):
        """
        返回对应页数据
        :param result:
        :param page:
        :param pageSize:
        :return:
        """
        page = int(self.count / self.pageSize)
        pageMax = page + 1
        pageNum = self.pageTotal - self.count
        #  如果传过来的总数量-实际查询的数量>=0,那么就需要取分页的数据
        if pageNum >= 0:
            result = self.result[(pageMax - 1) * 10: self.count]
        else:
            result = self.result[(page - 1) * 10:page * 10]
        return result

    def searchSqlFieldData(self, result, fields=None):
        """
        :param result: 数据库查询的queryset
        :param field: 需要返回给前端的字段,为一个列表;如果不传，则返回那个表的所有字段。
        :return: 返回查找出来数据库对应的字段
        """
        data_list = []
        if fields != None:
            for i in result:
                list_dict = dict.fromkeys(fields)
                for j in fields:
                    list_dict[j] = i.__dict__[j]
                    if isinstance(list_dict[j], datetime.datetime):
                        list_dict[j] = list_dict[j].strftime("%Y-%m-%d %H:%I:%S")
                data_list.append(list_dict)
        else:
            for i in result:
                new_dict = vars(i)
                for key in list(new_dict.keys()):
                    if key == '_state':
                        del new_dict[key]
                    elif isinstance(new_dict[key], datetime.datetime):
                        new_dict[key] = new_dict[key].strftime("%Y-%m-%d %H:%I:%S")
                data_list.append(new_dict)
        return data_list
