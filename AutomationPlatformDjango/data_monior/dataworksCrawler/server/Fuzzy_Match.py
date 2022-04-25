#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/7/11 15:38
# @Author : LiZongJie
# @Site : 
# @File : Fuzzy_Match.py
# @Software: PyCharm
import re


def project_fuzzy_match(table_name):
    if re.findall('rpt_sc_visual*', table_name):
        project_name = '供应链可视化'
    elif re.findall('rpt_rp_car_*', table_name) or re.findall('rpt_car_*', table_name):
        project_name = '车辆管家'
    elif re.findall('rpt_strategic*', table_name):
        project_name = '战略地图'
    elif re.findall('rpt_hkq_*', table_name):
        project_name = '好快全可视化'
    elif re.findall('rpt_storworker*', table_name):
        project_name = '技师档案'
    elif re.findall('rpt_workbench*', table_name) or re.findall('rpt_rp_workbench*', table_name) or re.findall(
            'rpt_sc_sku*',
            table_name) or re.findall(
        'rpt_sku*', table_name) or re.findall('comp_rpt_rp_workbench*', table_name):
        project_name = '前置仓工作台'
    elif re.findall('rpt_rp_visual*', table_name) or re.findall('rpt_visual*', table_name) or re.findall(
            'rpt_plog_workbench*', table_name) or re.findall('comp_rpt_rp_visual*', table_name):
        project_name = '前置仓可视化'
    elif re.findall('rpt_logistic*', table_name):
        project_name = '物流可视化'
    elif re.findall('rpt_ys*', table_name):
        project_name = '友商在线'
    elif re.findall('rpt_vendor*', table_name):
        project_name = '供应商交付绩效报表'
    elif re.findall('rpt_uc*', table_name) or re.findall('rpt_rp_store_revenue*', table_name) or re.findall(
            'rpt_rp_store_customer*', table_name):
        project_name = '天猫养车可视化'
        #re.findall('rpt_tmall*', table_name) or re.findall('rpt_rp_tmall*', table_name) or
    elif re.findall('rpt_rp_store_tmall*', table_name) or re.findall('rpt_car*', table_name):
        project_name = '天猫养车'
    elif re.findall('rpt_tag*', table_name) or re.findall('rpt_rp_customer*', table_name):
        project_name = '标签平台'
    elif re.findall('rpt_rp_kz_fact*', table_name) or re.findall('rpt_rp_kz_store_*', table_name):
        project_name = '经营分析看板'
    elif re.findall('rpt_rp_kz_franchisee*', table_name) or re.findall('rpt_store_sale*', table_name) or re.findall(
            'comp_rpt_rp_franchisee*', table_name) or re.findall('comp_rpt_rp_franchisee*', table_name):
        project_name = '加盟店'
    elif re.findall('rpt_rp_project*', table_name):
        project_name = '项目在线'
    elif re.findall('rpt_rp_uc*', table_name):
        project_name = '门店本地化'
    elif re.findall('rpt_rp_nj_logistics*', table_name):
        project_name = '物流大屏'
    elif re.findall('rpt_rp_kzapp*', table_name):
        project_name = '采购快报'
    elif re.findall('rpt_kz*', table_name) or re.findall('rpt_rp_kz_vendor*', table_name):
        project_name = '康众采红'
    elif re.findall('rpt_rp_int_warehouse*', table_name):
        project_name = '智能货柜报表'
    elif re.findall('rpt_rp_business_visual*', table_name):
        project_name = '事业部可视化'
    elif re.findall('rpt_rp_bdh*', table_name) or re.findall('rpt_plog_local*', table_name):
        project_name = '门店本地化'
    elif re.findall('rpt_luoshu*', table_name):
        project_name = '洛书产品'
    elif re.findall('rpt_prod*', table_name):
        project_name = '商品助手'
    elif re.findall('rpt_replenishment*', table_name):
        project_name = '货无忧'
    elif re.findall('rpt_rp_b2b*', table_name) or re.findall('rpt_b2b*', table_name):
        project_name = 'B2B电商'
    elif re.findall('rpt_rp_store_install*', table_name):
        project_name = '安装服务'
    elif re.findall('rpt_card*', table_name):
        project_name = '套餐卡'
    elif re.findall('rpt_finance*', table_name) or re.findall('rpt_rp_finance*', table_name):
        project_name = '财务报表'
    elif re.findall('rpt_intelligence_address*', table_name):
        project_name = '智能选址'
    elif re.findall('rpt_plog_search*', table_name):
        project_name = '智能搜索'
    elif re.findall('rpt_upkeep*', table_name):
        project_name = '机修项目'
    elif re.findall('rpt_ncarzone*', table_name):
        project_name = '新康众'
    elif re.findall('rpt_isco*', table_name):
        project_name = '库存共管'
    elif re.findall('dwd_trade_*', table_name) or re.findall('dws_trade_*', table_name) or re.findall(
            'dm_trade_*', table_name):
        project_name = '数仓-交易域'
    elif re.findall('dwd_stoworker_*', table_name) or re.findall('dws_stoworker_*', table_name) or re.findall(
            'dm_stoworker_*', table_name):
        project_name = '数仓-技师域'
    elif re.findall('dwd_store_*', table_name) or re.findall('dws_store_*', table_name) or re.findall(
            'dm_store_*', table_name):
        project_name = '数仓-维修厂域'
    elif re.findall('dwd_finance_*', table_name) or re.findall('dws_finance_*', table_name) or re.findall(
            'dm_finance_*', table_name):
        project_name = '数仓-财务域'
    elif re.findall('dwd_market*', table_name) or re.findall('dws_market*', table_name) or re.findall(
            'dm_market*', table_name):
        project_name = '数仓-营销域'
    elif re.findall('dwd_sc*', table_name) or re.findall('dws_sc*', table_name) or re.findall(
            'dm_sc*', table_name):
        project_name = '数仓-供应链域'
    elif re.findall('dwd_uc*', table_name) or re.findall('dws_uc*', table_name) or re.findall(
            'dm_uc*', table_name):
        project_name = '数仓-客户域'
    elif re.findall('dwd_car*', table_name) or re.findall('dws_car*', table_name) or re.findall(
            'dm_car*', table_name) or re.findall('dm_ali_car_*', table_name):
        project_name = '数仓-车辆域'
    elif re.findall('dwd_cus*', table_name) or re.findall('dws_cus*', table_name) or re.findall(
            'dm_cus*', table_name):
        project_name = '数仓-客服域'
    elif re.findall('dwd_plog*', table_name) or re.findall('dws_plog*', table_name) or re.findall(
            'dm_plog*', table_name):
        project_name = '数仓-用户行为域'
    elif re.findall('dwd_prod*', table_name) or re.findall('dws_prod*', table_name) or re.findall(
            'dm_prod*', table_name):
        project_name = '数仓-商品域'
    elif re.findall('dwd_keep*', table_name) or re.findall('dws_keep*', table_name) or re.findall(
            'dm_keep*', table_name):
        project_name = '数仓-履约域'
    elif re.findall('dwd_carowner*', table_name) or re.findall('dws_carowner*', table_name) or re.findall(
            'dm_carowner*', table_name):
        project_name = '数仓-车主域'
    elif re.findall('^ods_*', table_name):
        table = table_name.split('_')
        project_name = '源系统：' + table[2]
    elif re.findall('.*tmall_kpi*', table_name):
        project_name = '小二KPI罗盘'
    else:
        project_name = '未知'
    return project_name


def check_type_fuzzy_match(rulename):
    # rulename = rulename.encode('utf-8').decode('utf-8')
    if re.findall(r'.*波动.*', rulename):
        project_name = '数据波动类型监控'
    elif re.findall(r'.*重复.*', rulename) or re.findall(r'.*唯一.*', rulename):
        project_name = '重复数据监控'
    elif re.findall(r'.*空.*', rulename) or re.findall(r'.*0.*', rulename):
        project_name = '空值数据监控'
    elif re.findall(r'.*枚举.*', rulename) or re.findall(r'.*维度.*', rulename) or re.findall(
            r'.*离散.*', rulename):
        project_name = '枚举值数据监控'
    elif re.findall(r'.*额.*', rulename):
        project_name = '金额类数据监控'
    elif re.findall(r'.*数.*', rulename) or re.findall(r'.*量.*', rulename):
        project_name = '数值类数据监控'
    else:
        project_name = '其他业务异常数据监控'
    return project_name
