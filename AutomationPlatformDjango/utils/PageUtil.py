import datetime


class PageUtil:
    def getPageInfo(self, result, page=1, pageSize=10):
        """
        返回分页信息
        :param result:数据库查询的结果
        :param page:前端传的当前页
        :param pageSize:前端传的每页的页数
        :return:
        """
        pageInfo = dict()
        if isinstance(result, list):
            result_count = len(result)
        else:
            result_count = result.count()
        if result_count == 0:
            result_count = 0
        else:
            pageTotal = page * pageSize
            if result_count < pageTotal:
                pageInfo['pageMax'] = 1
            else:
                pageCount = int(result_count / pageSize)
                if result_count % pageSize > 0:
                    pageMax = pageCount + 1
                else:
                    pageMax = pageCount
                pageInfo['pageMax'] = pageMax
        pageInfo['page'] = page
        pageInfo['pageSize'] = pageSize
        pageInfo['pageTotal'] = result_count
        return pageInfo

    def getDataInfo(self, result, page=1, pageSize=10):
        """
        返回对应页数据
        :param result:
        :param page:
        :param pageSize:
        :return:
        """
        if isinstance(result, list):
            result_count = len(result)
        else:
            result_count = result.count()
        pageTotal = page * pageSize
        pageCount = int(result_count / pageSize)
        if result_count % pageSize > 0:
            pageMax = pageCount + 1
        else:
            pageMax = pageCount
        pageNum = pageTotal - result_count
        #  如果传过来的总数量-实际查询的数量>0,那么就需要取分页的数据
        if pageNum > 0:
            result = result[(pageMax - 1) * pageSize: result_count]
        else:
            result = result[(page - 1) * pageSize:page * pageSize]
        return result

    def dict2obj(self, obj, dict):
        obj.__dict__.update(dict)
        return obj

    def searchSqlFieldData(self, result, fields=None):
        """
        :param result: 数据库查询的queryset
        :param field: 需要返回给前端的字段,为一个列表;如果不传，则返回那个表的所有字段。
        :return: 返回查找出来数据库对应的字段的list
        """
        data_list = []
        if isinstance(result, list):
            return result
        if len(result) == 0:
            result = []
            return result
        else:
            if fields is not None:
                for i in result:
                    new_dict = vars(i)
                    if 'is_delete' in new_dict.keys():
                        is_delete = new_dict.get('is_delete')
                    else:
                        is_delete = 0
                    if int(is_delete) != 1:
                        list_dict = dict.fromkeys(fields)  # 通过传进来需要搜索返出去的字段新建一个字典
                        for j in fields:
                            list_dict[j] = i.__dict__[j]
                            if isinstance(list_dict[j], datetime.datetime):
                                list_dict[j] = list_dict[j].strftime("%Y-%m-%d %H:%I:%S")
                    else:
                        continue
                    data_list.append(list_dict)
            else:
                for i in result:
                    new_dict = i
                    if not isinstance(i, dict):
                        new_dict = vars(i)
                    for key in list(new_dict.keys()):
                        if key == '_state':
                            del new_dict[key]
                        elif isinstance(new_dict[key], datetime.datetime):
                            new_dict[key] = new_dict[key].strftime("%Y-%m-%d %H:%I:%S")
                    if 'is_delete' in new_dict.keys():
                        if int(new_dict.get('is_delete')) != 1:
                            data_list.append(new_dict)
                    else:
                        data_list.append(new_dict)
                        pass
        return data_list
