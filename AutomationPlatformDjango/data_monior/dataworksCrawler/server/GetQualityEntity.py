#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/6/24 10:31
# @Author : LiZongJie
# @Site : 
# @File : GetQualityEntity.py
# 获取分区表达式id
# @Software: PyCharm

class GetEntity:
    def __init__(self):
        pass

    @staticmethod
    def main(
            tables, name_owner,api
    ) -> None:
        res = tables.copy()
        new_table_list = []
        # new_tables = tables.copy()
        try:
            dict_result = api.GetQualityEntity(tables)
            if len(dict_result['Data']) != 0:
                for i in dict_result['Data']:
                    res = tables.copy()
                    res['table_id'] = i['Id']
                    res['accountname'] = i['OnDutyAccountName'][0:3]
                    try:
                        res['accountnameid'] = name_owner[i['OnDutyAccountName'][0:3]]
                    except:
                        res['accountnameid'] = ''
                    res['status'] = 0
                    res['description'] = '成功'
                    new_table_list.append(res)
            else:
                res['table_id'] = ''
                res['accountname'] = ''
                res['accountnameid'] = ''
                res['status'] = 2
                res['description'] = '未配置数据预警'
                new_table_list.append(res)
        except Exception as f:
            res['table_id'] = ''
            res['accountname'] = ''
            res['accountnameid'] = ''
            res['status'] = 1
            res['description'] = 'GetQualityEntity报错'
            new_table_list.append(res)
        return new_table_list

    # @staticmethod
    # async def main_async(
    #         tables,
    # ) -> None:
    #     client = Sample.create_client('LTAI4GHKZBiC7EPpCjuN1kNU', 'fSw1Od5gNfDOz4WJs5b8bmLmtBCQQL')
    #     get_quality_entity_request = dataworks_public_20200518_models.GetQualityEntityRequest(
    #         table_name=tables.get('table_name'),
    #         project_name=tables.get('table_schema'),
    #         env_type='odps'
    #     )
    #     # 复制代码运行请自行打印 API 的返回值
    #     await client.get_quality_entity_async(get_quality_entity_request)

# if __name__ == '__main__':
#     owner_name = {
#         '333503': '苏茂成', '188772': '陈樟涛', '322142': '张翔翔', '323251': '牛百阳', '323654': '杜康', '333541': '邵百川',
#         '323653': '张敬超', '703240': '周龙'
#     }
#     name_owner = dict([val, key] for key, val in owner_name.items())
#     table_dict = {
#         'table_name': 'rpt_rp_business_visual_performance_month_d',
#         'table_schema': 'nczbigdata'
#     }
#     result = Sample.main(table_dict,name_owner)  # ods_src_item_ic_item_franch dws_prod_sku_order_day_2c
#     print(result)
