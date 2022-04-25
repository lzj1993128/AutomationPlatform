from django.db import models
from api.models import User, Project, Module, Database

# Create your models here.
IS_DELETE = ((0, False), (1, True))


class BigData(models.Model):
    big_data_id = models.AutoField(primary_key=True, null=False)
    big_data_name = models.CharField(max_length=50, verbose_name='大数据名称')
    project = models.ForeignKey('api.Project', on_delete=models.CASCADE)
    module = models.ForeignKey('api.Module', on_delete=models.CASCADE)
    db = models.ForeignKey('api.Database', on_delete=models.CASCADE)
    requestCompareFieldList = models.TextField(default=None, verbose_name='指标字段列表')
    request_method = models.CharField(max_length=10, null=True, verbose_name='http请求或者dubbo请求')
    api_name = models.CharField(max_length=200, verbose_name='http接口名称')
    api_url = models.CharField(max_length=200, null=True, default=None, verbose_name='http接口url')
    method = models.CharField(max_length=20, null=True, default=None, verbose_name='http接口请求方式')
    data_type = models.CharField(max_length=20, null=True, default=None, verbose_name='http数据传输方式')
    requestHeader = models.TextField(default=None, null=True, verbose_name='http请求header')
    requestBody = models.TextField(default=None, null=True, verbose_name='http请求body')
    reponse_field = models.CharField(max_length=200, default=None, verbose_name='返回结果中包含所有指标数据的那个key')
    zk_database = models.CharField(max_length=200, null=True, default=None, verbose_name='zk注册服务器')
    zk_api_name = models.CharField(max_length=200, null=True, default=None, verbose_name='服务接口名')
    zk_api_method = models.CharField(max_length=200, null=True, default=None, verbose_name='服务方法名')
    requestJson = models.TextField(default=None, null=True, verbose_name='json请求参数')
    report_database_name = models.CharField(max_length=100, verbose_name='指标报表名字')
    sql = models.TextField(default=None, verbose_name='sql语句')
    description = models.CharField(max_length=100, null=True, verbose_name='接口描述')
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    last_updata_person = models.CharField(max_length=50, null=True, verbose_name='最后更新人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')
    RESULT_CHOICE = ((0, '未运行'), (1, '运行中'), (2, '运行结束'), (3, '运行异常'))
    run_status = models.CharField(max_length=50, verbose_name='运行状态', default=0, choices=RESULT_CHOICE)


class BigDataHistory(models.Model):
    big_data_his_id = models.AutoField(primary_key=True, null=False)
    big_data = models.ForeignKey('BigData', on_delete=models.CASCADE)
    big_data_his_name = models.CharField(max_length=50, default=None, verbose_name='大数据名称')
    total_compare_nums = models.IntegerField(null=True, verbose_name='比较执行总数')
    pass_compare_nums = models.IntegerField(null=True, verbose_name='比较通过数')
    fail_compare_nums = models.IntegerField(null=True, verbose_name='比较失败数')
    error_compare_nums = models.IntegerField(null=True, verbose_name='比较错误数')
    pass_compare_pers = models.FloatField(null=True, verbose_name='通过率')
    total_api_nums = models.IntegerField(null=True, verbose_name='执行api总数')
    pass_api_nums = models.IntegerField(null=True, verbose_name='api通过数')
    fail_api_nums = models.IntegerField(null=True, verbose_name='api失败数')
    error_api_nums = models.IntegerField(null=True, verbose_name='api错误数')
    pass_api_pers = models.FloatField(null=True, verbose_name='api通过率')
    report = models.IntegerField(null=True,default=None,verbose_name='报告id')
    csv_file_name = models.CharField(max_length=100, default=None, null=True, verbose_name='压缩包名字')
    csv_file_path = models.CharField(max_length=200, default=None, null=True, verbose_name='压缩包路径')
    operator = models.CharField(max_length=50, null=True, default='sys', verbose_name='操作人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')


class JsonDataBank(models.Model):
    json_data_bank_id = models.AutoField(primary_key=True, null=False)
    json_data_bank_name = models.TextField(default=None, verbose_name='json数据集合名称')
    description = models.CharField(max_length=100, null=True, verbose_name='描述')
    last_updata_person = models.CharField(max_length=50, null=True, verbose_name='最后更新人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')
