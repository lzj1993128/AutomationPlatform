# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # @Time : 2021/8/3 11:13
# # @Author : LiZongJie
# # @Site :
# # @File : ListInstance.py
# # @Software: PyCharm
# # !/usr/bin/env python
# # coding=utf-8
# from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.request import CommonRequest
# from aliyunsdkcore.auth.credentials import AccessKeyCredential
# import datetime
# import time
# import pandas as pd
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from data_monior.dataworksTableCheck.servers.sendDingtalk import sendDingTalk
#
# pd.set_option('display.max_columns', None)
#
#
# class RT_Task(object):
#     def __init__(self):
#         '''
#         固定取10分钟内的报警情况数据
#         start：10分钟前时间
#         end：当前时间
#         '''
#         credentials = AccessKeyCredential('LTAI4G93f6qxFogEQR3Y5eh2', 'vYwFn8N8nWIVqFEncq0LGmr7ov5dMM')
#         self.client = AcsClient(region_id='cn-shanghai', credential=credentials)
#         # self.client = AcsClient('LTAI4G93f6qxFogEQR3Y5eh2', 'vYwFn8N8nWIVqFEncq0LGmr7ov5dMM', 'cn-shanghai')
#         self.end = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         self.start = (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
#         self.nowMinuteTimeStamp = int(time.mktime(datetime.datetime.now().timetuple())) * 1000
#         self.tenMinuteBeforeTimeStamp = int(
#             time.mktime((datetime.datetime.now() - datetime.timedelta(minutes=10)).timetuple())) * 1000
#
#     def getmetriclist(self, projectName, jobNameList, indicator):
#         '''
#         拼接任务请求
#         :param projectName: 项目名称
#         :param jobNameList: 实时任务表名列表
#         :param indicator: 延时：delay  作业失败率：task_failover.rate
#         :return:
#         '''
#         metriclist = []
#         for i in jobNameList:
#             for j in indicator:
#                 metricdict = {}
#                 metricdict['projectName'] = projectName
#                 metricdict['jobName'] = i
#                 metricdict['indicator'] = j
#                 metricdict['metric'] = 'blink.{projectName}.{jobName}.{indicator}'.format(projectName=projectName,
#                                                                                           jobName=i,
#                                                                                           indicator=j)
#                 metriclist.append(metricdict)
#         return metriclist
#
#     def resultJudge(self, indicator, res):
#         '''
#         结果判断
#         :param indicator:
#         :param res:
#         :return:
#         '''
#         error = 0
#         error_des = ''
#         if indicator == 'delay':
#             if max(res.values()) > 30 * 60 * 1000:  # 30 * 60 * 1000
#                 # 判断延时大于30分钟，转化为毫秒级时间戳
#                 error_des = '延时大于30分钟'
#                 error = 1
#         if indicator == 'task_failover.rate':
#             result = list(res.values())
#             if len([i for i in result if i > 0]) > 3:
#                 # 判断是否存在三次报错
#                 error_des = '报错三次以上'
#                 error = 1
#         return error_des, error
#
#     def listinstance(self):
#         '''
#         获取某个project下所有的运行实例
#         :return:
#         '''
#         request = CommonRequest()
#         request.set_accept_format('json')
#         request.set_method('GET')
#         request.set_protocol_type('https')  # https | http
#         request.set_domain('foas.cn-shanghai.aliyuncs.com')
#         request.set_version('2018-11-11')
#         request.add_query_param('pageSize', "100")
#         request.add_query_param('pageIndex', "1")
#         request.add_query_param('jobType', "FLINK_STREAM")
#         request.add_header('Content-Type', 'application/json')
#         request.set_uri_pattern('/api/v2/projects/ncz_dashboard/instances')
#         body = '''{}'''
#         request.set_content(body.encode('utf-8'))
#         response = self.client.do_action_with_exception(request)
#         response = str(response, encoding='utf-8')
#         response = eval(response)
#         result = response['Instances']['Instance']
#         df = pd.DataFrame(result)
#         df = df[df['ActualState'] != 'TERMINATED']
#         df = df[~df.JobName.str.contains('test')]
#         # print(df)
#         JobNameList = df['JobName'].tolist()
#         # print(JobNameList)
#         # df.to_csv('job.csv')
#         return JobNameList
#
#     def GetInstanceMetric(self, metricdict):
#         '''
#         您可以通过GetInstanceMetric获取正在运行实例的所有Metric信息。
#         :return:
#         '''
#         # client = AcsClient('<accessKeyId>', '<accessSecret>', 'cn-shanghai')
#         projectName = metricdict['projectName']
#         jobName = metricdict['jobName']
#         metric = metricdict['metric']
#         indicator = metricdict['indicator']
#         uri_pattern = '/api/v2/projects/{projectName}/jobs/{jobName}/metric'.format(projectName=projectName,
#                                                                                     jobName=jobName)
#         request = CommonRequest()
#         request.set_accept_format('json')
#         request.set_method('POST')
#         request.set_protocol_type('https')  # https | http
#         request.set_domain('foas.cn-shanghai.aliyuncs.com')
#         request.set_version('2018-11-11')
#         request.add_header('Content-Type', 'application/json')
#         request.set_uri_pattern(uri_pattern)
#         body = '''{\"metricJson\":\"{\\"start\\":%s,\\"end\\":%s,\\"limit\\":\\"avg:sample:50\\",\\"queries\\":[{\\"downsample\\":\\"20s-avg\\",\\"metric\\":\\"%s\\",\\"granularity\\":\\"20s\\",\\"aggregator\\":\\"max\\"}]}\"}''' % (
#             self.tenMinuteBeforeTimeStamp, self.nowMinuteTimeStamp, metric)
#         request.set_content(body.encode('utf-8'))
#         response = self.client.do_action_with_exception(request)
#         response = eval(str(response, 'utf-8'))
#         res = response['Metrics']['Metric'][0]['Dps']
#         error_des, error = self.resultJudge(indicator, res)
#         metricdict['error_des'] = error_des
#         metricdict['error'] = error
#         return metricdict
#
#     def resultDataFrame(self, result):
#         # 处理实时任务报错dataframe数据
#         failoverlist = [i for i in result if i['indicator'] == 'task_failover.rate']
#         failoverlist_df = pd.DataFrame(failoverlist)
#         failoverlist_df['failover'] = failoverlist_df['error_des']
#         failoverlist_df['failover_error'] = failoverlist_df['error']
#         new_failoverlist_df = failoverlist_df[['projectName', 'jobName', 'failover', 'failover_error']]
#         # print(new_failoverlist_df)
#         # 处理实时任务延时dataframe数据
#         delaylist = [i for i in result if i['indicator'] == 'delay']
#         delaylist_df = pd.DataFrame(delaylist)
#         delaylist_df['delay'] = delaylist_df['error_des']
#         delaylist_df['delay_error'] = delaylist_df['error']
#         new_delaylist_df = delaylist_df[['projectName', 'jobName', 'delay', 'delay_error']]
#         # print(new_delaylist_df)
#         df_result = pd.merge(new_failoverlist_df, new_delaylist_df, on=['jobName'])
#         df_result = df_result[(df_result['failover_error'] > 0) | (df_result['delay_error'] > 0)]
#         df_result = df_result[['projectName_x', 'jobName', 'failover', 'delay']]
#         df_result.columns = ['项目', '任务名', '报错', '延时']
#         return df_result
#
#     def run(self, webhook=None, at_mobiles=None):
#         projectName = 'ncz_dashboard'
#         jobNameList = self.listinstance()
#         indicator = ['delay', 'task_failover.rate']  # 延时：delay  作业失败率：task_failover.rate
#         getmetriclist = self.getmetriclist(projectName, jobNameList, indicator)
#         # print(getmetriclist)
#         max_workers = 5
#         executor = ThreadPoolExecutor(max_workers=max_workers)  # 创建线程池
#         all_task = [executor.submit(self.GetInstanceMetric, metric) for metric in getmetriclist]
#         result = []
#         for future in as_completed(all_task):
#             try:
#                 data = future.result()
#                 result.append(data)
#             except:
#                 continue
#         df_result = self.resultDataFrame(result)
#         df_empty = df_result.empty
#         if df_empty:
#             pass
#         else:
#             sendDT = sendDingTalk()
#             sendDT.generate_images(df_result)
#             file = sendDT.upload_image()
#             sendDT.send_blink_dingrobot( webhook, file, at_mobiles, self.start, self.end)
#         # import dataframe_image as dfi
#         # import matplotlib.pyplot as plt
#         # plt.rcParams['font.sans-serif'] = ['simhei']
#         # dfi.export(df_result, '20210804.jpg', table_conversion='matplotlib')
#
# # if __name__ == '__main__':
# #     client = RT_Task()
# #     # accesskey = '4082f4dfda66f77cfb525561bd14fd208422bc18a3b6d499ffe9f8e7ad571297'
# #     # at_mobiles = ['17600035316']
# #     client.run()
