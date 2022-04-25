# from datetime import datetime
#
# from cron_descriptor import get_description
# from croniter import croniter
#
#
# class CronUtil:
#     def handleCron(self, cron, times=5):
#         """
#         默认返回5个时间
#         :param cron:
#         :param times:
#         :return:
#         """
#         try:
#             cron = croniter(cron, datetime.now())
#             nextTime = [cron.get_next(datetime).strftime('%Y-%m-%d %H:%M:%S') for i in range(times)]
#             return nextTime
#         except:
#             raise Exception('表达式不支持')
#
#     def getCronDesc(self, cron):
#         """
#         获取表达式的意思
#         :param cron:
#         :return:
#         """
#         try:
#             cronDesc = get_description('*' + ' ' + cron)
#             return cronDesc
#         except:
#             raise Exception('表达式不支持')
