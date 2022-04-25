import datetime

from django.db import connections


class DatabaseUtil(object):

    def sql_to_dict(self, sql, params=None, db='default'):
        """
        返回全部数据
        :param sql: sql语句
        :param params: sql语句参数
        :param db: Django数据库名
        :return: 例如：[{"id": id}]
        """
        cursor = connections[db].cursor()
        cursor.execute(sql, params)
        desc = cursor.description
        object_list = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
        for i in object_list:
            if isinstance(i, dict):
                for key in i.keys():
                    if isinstance(i[key], datetime.datetime):
                        i[key] = i[key].strftime("%Y-%m-%d %H:%I:%S")
        cursor.close()
        return object_list

    def sqlResult(self, sql, db='default'):
        """
        返回sql执行结果,返回实际结果，如sum啥的
        :param sql:
        :param db:
        :return:
        """
        cursor = connections[db].cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        result = result[0]
        cursor.close()
        return result
