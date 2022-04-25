# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # @Time : 2021/9/17 14:06
# # @Author : LiZongJie
# # @Site :
# # @File : dataWorksApi.py
# # @Software: PyCharm
#
# import datetime
# from alibabacloud_dataworks_public20200518.client import Client as dataworks_public20200518Client
# from alibabacloud_tea_openapi import models as open_api_models
# from alibabacloud_dataworks_public20200518 import models as dataworks_public_20200518_models
# import math
#
#
# class Sample:
#     def __init__(self, user, password):
#         self.client = self.create_client(user, password)
#
#     def create_client(self,
#                       access_key_id: str,
#                       access_key_secret: str,
#                       ) -> dataworks_public20200518Client:
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
#         config.endpoint = 'dataworks.cn-shanghai.aliyuncs.com'
#         return dataworks_public20200518Client(config)
#
#     def getTableBasicInfo(self, table):
#         '''
#         获取表基本信息：表创建时间、上次修改时间、生命周期、表名、创建者、表大小
#         :param table:
#         :return: resDict = {'CreateTime': 创建时间, 'LastDdlTime': 最近一次变更表结构的时间, 'LastModifyTime': 最近一次更新表的时间,
#                    'LifeCycle': 表的生命周期, 'DataSize': 表占用的存储空间(GB), 'Comment': 表的描述, 'OwnerId': 表所有者的ID}
#         '''
#         get_meta_table_basic_info_request = dataworks_public_20200518_models.GetMetaTableBasicInfoRequest(
#             table_guid='odps.' + table
#         )
#         # 复制代码运行请自行打印 API 的返回值
#         result = self.client.get_meta_table_basic_info(get_meta_table_basic_info_request)
#         dict_result = result.body.to_map()
#         table_result = dict_result['Data']
#         CreateTime = str(datetime.datetime.fromtimestamp(int(str(table_result['CreateTime'])[0:-3])))
#         LastDdlTime = str(datetime.datetime.fromtimestamp(int(str(table_result['LastDdlTime'])[0:-3])))
#         LastModifyTime = str(datetime.datetime.fromtimestamp(int(str(table_result['LastModifyTime'])[0:-3])))
#         LifeCycle = table_result['LifeCycle']
#         Comment = table_result['Comment']
#         try:
#             OwnerId = table_result['OwnerId']
#         except:
#             OwnerId = '未知'
#         DataSize = str(format(table_result['DataSize'] / 1024 / 1024 / 1024, '.4f')) + 'GB'
#         resDict = {'CreateTime': CreateTime, 'LastDdlTime': LastDdlTime, 'LastModifyTime': LastModifyTime,
#                    'LifeCycle': LifeCycle, 'DataSize': DataSize, 'Comment': Comment, 'OwnerId': OwnerId}
#         return resDict
#
#     def getTableOwnerList(self, project_id):
#         '''
#         获取DataWorks工作空间中已存在成员的列表
#         :param project_id:
#         :return:
#         '''
#
#         def getTableOwner(project_id, page_number=1):
#             list_project_members_request = dataworks_public_20200518_models.ListProjectMembersRequest(
#                 project_id=project_id,
#                 page_number=page_number
#             )
#             # 复制代码运行请自行打印 API 的返回值
#             result = self.client.list_project_members(list_project_members_request)
#             dict_result = result.body.to_map()
#             table_result = dict_result['Data']
#             return table_result, page_number
#
#         table_result, page_number = getTableOwner(project_id)
#         page_number = page_number + 1
#         MemberList = table_result['ProjectMemberList']
#         while math.ceil(table_result['TotalCount'] / table_result['PageSize']) >= table_result['PageNumber']:
#             table_result, page_number = getTableOwner(project_id, page_number)
#             ProjectMemberList = table_result['ProjectMemberList']
#             MemberList = ProjectMemberList + MemberList
#             page_number += 1
#         return MemberList
#
#     def getProjects(self):
#         '''
#         获取租户下的DataWorks工作空间列表
#         :return:
#         '''
#         list_projects_request = dataworks_public_20200518_models.ListProjectsRequest()
#         # 复制代码运行请自行打印 API 的返回值
#         result = self.client.list_projects(list_projects_request)
#         dict_result = result.body.to_map()
#         res = dict_result['PageResult']['ProjectList']
#         pro_id = {i['ProjectIdentifier']: i['ProjectId'] for i in res}
#         return pro_id
#
#     def getProjectsOwner(self, project):
#         pro_id = self.getProjects()
#         project_id = pro_id[project]
#         ownerList = self.getTableOwnerList(project_id)
#         ownerdict = {i['ProjectMemberId']: i['Nick'] for i in ownerList}
#         ownerdict['未知'] = '未知'
#         # print(ownerdict)
#         return ownerdict
#
#     def ListQualityResultsByEntity(self, table_id, start_date, end_date, tables):
#         list_quality_results_by_entity_request = dataworks_public_20200518_models.ListQualityResultsByEntityRequest(
#             entity_id=table_id,
#             start_date=start_date,
#             end_date=end_date,
#             project_name=tables.get('table_schema'),
#             page_size=20,
#             page_number=1
#         )
#         # 复制代码运行请自行打印 API 的返回值
#         result = self.client.list_quality_results_by_entity(list_quality_results_by_entity_request)
#         dict_result = result.body.to_map()
#         # table_result = dict_result['Data']['RuleChecks']
#         return dict_result['Data']['RuleChecks']
#
#     def GetQualityEntity(self, tables):
#         get_quality_entity_request = dataworks_public_20200518_models.GetQualityEntityRequest(
#             table_name=tables.get('table_name'),  # 'comp_trade_ods_5min_job'
#             project_name=tables.get('table_schema'),
#             env_type='odps'
#         )
#         # 复制代码运行请自行打印 API 的返回值
#         result = self.client.get_quality_entity(get_quality_entity_request)
#         dict_result = result.body.to_map()
#         print(dict_result)
#         return dict_result
# # user = 'LTAI4GHKZBiC7EPpCjuN1kNU'
# # password = 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL'
# # table = 'nczbigdata.ods_src_tag_platform_tagplatform_tag_info'
# # request = Sample(user, password)
# # project_id = 97716
# # project = 'nczbigdata'
# # res = request.getProjectsOwner(project)
