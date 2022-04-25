#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/24 18:42
# @Author : LiZongJie
# @Site : 
# @File : ListQualityRules.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import sys

from typing import List

from alibabacloud_dataworks_public20200518.client import Client as dataworks_public20200518Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dataworks_public20200518 import models as dataworks_public_20200518_models


class Rule_Num:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> dataworks_public20200518Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = 'dataworks.cn-shanghai.aliyuncs.com'
        return dataworks_public20200518Client(config)

    @staticmethod
    def main(
            entity_id,
    ) -> None:
        client = Rule_Num.create_client('LTAI4GHKZBiC7EPpCjuN1kNU', 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL')
        list_quality_rules_request = dataworks_public_20200518_models.ListQualityRulesRequest(
            entity_id=entity_id,
            project_name='nczbigdata',
            page_number=1,
            page_size=20
        )
        # 复制代码运行请自行打印 API 的返回值
        result = client.list_quality_rules(list_quality_rules_request)
        dict_result = result.body.to_map()
        rule_num = dict_result['Data']['TotalCount']
        # print(rule_num)
        return rule_num
        # table_result = dict_result['Data']['RuleChecks']

    @staticmethod
    async def main_async(
            entity_id,
    ) -> None:
        client = Rule_Num.create_client('LTAI4GHKZBiC7EPpCjuN1kNU', 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL')
        list_quality_rules_request = dataworks_public_20200518_models.ListQualityRulesRequest(
            entity_id=entity_id,
            project_name='nczbigdata',
            page_number=1,
            page_size=20
        )
        # 复制代码运行请自行打印 API 的返回值
        await client.list_quality_rules_async(list_quality_rules_request)

# if __name__ == '__main__':
#     Rule_Num.main('1539695')
