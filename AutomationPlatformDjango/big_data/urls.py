from django.conf.urls import url

from big_data.views.big_data.BigDataHistoryView import *
from big_data.views.big_data.BigDataView import *

urlpatterns = [
    # 大数据模块
    url('big_data/add', addBigData),
    url('big_data/search', searchBigData),
    url('big_data/run', runBigDataCompare),
    url('big_data/delete', deleteBigData),
    url('big_data/testRun', testRunRequest),
    url('big_data/getBigData', getBigData),


    # 大数据历史页
    url('big_data_history/download', downloadBigDataHistory),
    url('big_data_history/search', searchBigHistory)
]
