# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # @Time : 2021/10/15 14:58
# # @Author : LiZongJie
# # @Site :
# # @File : analysisSql.py
# # @Software: PyCharm
# import sqlparse
# import re
# import sqlparser
#
#
# class sqlParse(object):
#     def clean(self, sql_str):
#         # remove the /* */ comments
#         q = re.sub(r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/", "", sql_str)
#         # remove whole line -- and # comments
#         lines = [line for line in q.splitlines() if not re.match("^\s*(--|#)", line)]
#         # remove trailing -- and # comments
#         q = " ".join([re.split("--|#", line)[0] for line in lines])
#         q = ' '.join(q.split())
#         return q
#
#     def get_query_columns(self, sql):
#         '''Return a list of column headers from given sqls select clause'''
#
#         columns = []
#         parser = sqlparser.Parser(vendor=2)
#         # Parser does not like new lines
#         # print(sql)
#         sql2 = self.clean(sql)
#         # sql3 = sql.replace('\n', '').replace('\r', '')
#         # print('sql3',sql3)
#         # print('sql2',sql2)
#         # print(parser.check_syntax(sql2))
#         # Check for syntax errors
#         if parser.check_syntax(sql2)[0] != 0:
#             raise Exception('SQL语法不正确')
#         stmt = parser.get_statement(0)
#         root = stmt.get_root()
#         qcolumns = root.__dict__['resultColumnList']
#         for qcolumn in qcolumns.list:
#             if qcolumn.aliasClause:
#                 alias = qcolumn.aliasClause.get_text()
#                 columns.append(alias)
#             else:
#                 name = qcolumn.get_text()
#                 name = name.split('.')[-1]  # remove table alias
#                 columns.append(name)
#         return columns
