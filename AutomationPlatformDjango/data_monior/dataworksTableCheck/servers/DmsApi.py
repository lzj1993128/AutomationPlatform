#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/11/17 17:30
# @Author : LiZongJie
# @Site : 
# @File : DmsApi.py
# @Software: PyCharm
# from alibabacloud_dms_enterprise20181101.client import Client as dms_enterprise20181101Client
# from alibabacloud_tea_openapi import models as open_api_models
# from alibabacloud_dms_enterprise20181101 import models as dms_enterprise_20181101_models

#
# class DmsApi:
#     def __init__(self, user, password):
#         self.client = self.create_client(user, password)
#
#     # def __init__(self):
#     #     pass
#     def create_client(self,
#                       access_key_id: str,
#                       access_key_secret: str,
#                       ) -> dms_enterprise20181101Client:
#         """
#         使用AK&SK初始化账号Client
#         @param access_key_id:
#         @param access_key_secret:
#         @return: Client
#         @throws Exception
#         """
#         config = open_api_models.Config(
#             # 您的AccessKey ID,
#             access_key_id=access_key_id,
#             # 您的AccessKey Secret,
#             access_key_secret=access_key_secret
#         )
#         # 访问的域名
#         config.endpoint = 'dms-enterprise.aliyuncs.com'
#         return dms_enterprise20181101Client(config)
#
#     def sqlquery(self, sql):
#         # client = Sample.create_client('LTAI4GHKZBiC7EPpCjuN1kNU', 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL')
#         execute_script_request = dms_enterprise_20181101_models.ExecuteScriptRequest(
#             logic=False,
#             db_id=2251455,
#             script=sql
#         )
#         # 复制代码运行请自行打印 API 的返回值
#         res = self.client.execute_script(execute_script_request)
#         dict_result = res.body.to_map()
#         return dict_result['Results'][0]['Rows']
