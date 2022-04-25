from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# 逻辑删除
IS_DELETE = ((0, '否'), (1, '是'))


class User(AbstractUser):
    """
    用户管理
    """
    user_id = models.AutoField(primary_key=True, null=False)
    token = models.CharField(max_length=200, null=True, default=None)
    nickname = models.CharField(max_length=200, null=True, default=None, verbose_name='用户昵称')
    role = models.ForeignKey('Role', default=1, on_delete=models.CASCADE)
    last_login_ip = models.CharField(max_length=50, null=True, default=None, verbose_name='最后登录IP')
    login_count = models.IntegerField(null=True, default=0, verbose_name='不同ip登录统计')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    ac_token = models.CharField(max_length=100, null=True, default=None, verbose_name='actoken')
    phone = models.CharField(max_length=30, null=True, default=None, verbose_name='手机号')

    def __str__(self):
        return self.username


class Role(models.Model):
    """
    用户角色表
    """
    role_id = models.AutoField(primary_key=True, null=False)
    role_name = models.CharField(max_length=50, null=True, default=True)


class Business(models.Model):
    """
    业务域管理
    """
    bd_id = models.AutoField(primary_key=True, null=False)
    bd_name = models.CharField(max_length=50, verbose_name='业务域名称')
    description = models.CharField(max_length=100, null=True, verbose_name='业务域描述')
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')


class Project(models.Model):
    """
    项目管理
    """
    prj_id = models.AutoField(primary_key=True, null=False)
    prj_name = models.CharField(max_length=50, verbose_name='项目名称')
    robot_group_id = models.IntegerField(null=True, default=None, verbose_name='机器人群组id')
    description = models.CharField(max_length=100, null=True, verbose_name='项目描述')
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')

    def __str__(self):
        return self.prj_name


class Module(models.Model):
    """
    模块管理
    """
    module_id = models.AutoField(primary_key=True, null=False)
    module_name = models.CharField(max_length=50, verbose_name='模块名称')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')

    def __str__(self):
        return self.module_name


class Interface(models.Model):
    """
    接口管理
    """
    api_id = models.AutoField(primary_key=True, null=False)
    api_name = models.TextField(verbose_name='接口名称')
    api_url = models.CharField(max_length=200, verbose_name='接口地址')
    method = models.CharField(max_length=4, verbose_name='请求方式,get或者post')
    data_type = models.CharField(max_length=4, verbose_name='数据传输方式')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    description = models.CharField(max_length=100, null=True, verbose_name='接口描述')
    request_header_param = models.TextField(null=True, verbose_name='请求头参数')
    request_body_param = models.TextField(null=True, verbose_name='请求body参数')
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')
    is_sign = models.BooleanField(default=False, verbose_name='是否需要签名')
    request_method = models.CharField(max_length=10, null=True, default=None, verbose_name='http或者dubbo请求')
    zk_database = models.CharField(max_length=200, null=True, default=None, verbose_name='zk注册服务器')
    zk_api_name = models.CharField(max_length=200, null=True, default=None, verbose_name='服务接口名')
    zk_api_method = models.CharField(max_length=200, null=True, default='', verbose_name='服务方法名')
    requestJsonList = models.TextField(default=None, null=True, verbose_name='json请求参数')
    developer = models.CharField(max_length=20, default=None, null=True, verbose_name='开发者')

    def __str__(self):
        return self.api_name


class Case(models.Model):
    """
    用例管理
    """
    case_id = models.AutoField(primary_key=True, null=False)
    case_name = models.CharField(max_length=50)
    CASE_TYPE = ((0, '单接口用例'), (1, '流程接口用例'), (2, '公共接口用例'), (3, '数据驱动用例'))
    case_type = models.CharField(choices=CASE_TYPE, default=0, max_length=20, verbose_name='用例类型')
    ONlINE_TYPE = ((0, False), (1, True))
    #  0 表示只能测试环境运行，1 可以在线上运行
    online_type = models.CharField(choices=ONlINE_TYPE, default=0, max_length=20, verbose_name='线上执行')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True, verbose_name='用例描述')
    api_list = models.TextField(default='', verbose_name='包含接口')
    step_info = models.TextField(default=None, verbose_name="存前端传过来的步骤值")
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    update_person = models.CharField(max_length=50, null=True, verbose_name='更新人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')
    bd_id = models.IntegerField(null=True, verbose_name='业务id')
    case_nums = models.IntegerField(null=True, verbose_name='用例数')

    def __str__(self):
        return self.case_name


class CaseLog(models.Model):
    """
    用例操作日志
    """
    log_id = models.AutoField(primary_key=True, null=False)
    case_id = models.IntegerField(null=True, verbose_name='用例id')
    case_name = models.CharField(max_length=50)
    CASE_TYPE = ((0, '单接口用例'), (1, '流程接口用例'), (2, '公共接口用例'), (3, '数据驱动用例'))
    case_type = models.CharField(choices=CASE_TYPE, default=0, max_length=20, verbose_name='用例类型')
    ONlINE_TYPE = ((0, False), (1, True))
    #  0 表示只能测试环境运行，1 可以在线上运行
    online_type = models.CharField(choices=ONlINE_TYPE, default=0, max_length=20, verbose_name='线上执行')
    api_list = models.TextField(default='', verbose_name='包含接口')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True, verbose_name='用例描述')
    step_info = models.TextField(default=None, verbose_name="存前端传过来的步骤值")
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    bd_id = models.IntegerField(null=True, verbose_name='业务id')

    class Meta:
        db_table = 'case_log'


class ApiResult(models.Model):
    """
    调试过程中接口接口返回暂存
    """
    api_id = models.CharField(max_length=11, null=True, verbose_name='接口id')
    content = models.TextField()
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.api_id


class CaseResult(models.Model):
    """
    调试过程中用例结果返回暂存
    """
    case_id = models.CharField(max_length=11, null=True, verbose_name='Caseid')
    content = models.TextField()
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.case_id


class Plan(models.Model):
    """
    任务表
    """
    plan_id = models.AutoField(primary_key=True, null=False)
    plan_name = models.CharField(max_length=50, verbose_name='计划名称')
    is_enable = models.BooleanField(default=0, verbose_name='是否启用')
    ONlINE_TYPE = ((0, '测试'), (1, '线上'))
    #  0 表示只能测试环境运行，1 可以在线上运行
    online_type = models.SmallIntegerField(choices=ONlINE_TYPE, default=0, verbose_name='线上执行')
    CASE_TYPE = ((0, '项目'), (1, '接口用例'), (2, '大数据用例'))
    case_type = models.SmallIntegerField(choices=CASE_TYPE, default=0, verbose_name='选择的执行用例类型')
    description = models.CharField(max_length=200, null=True, verbose_name='计划描述')
    run_time_start = models.CharField(max_length=200, default=None, verbose_name='运行时间段开始')
    run_time_end = models.CharField(max_length=200, default=None, verbose_name='运行时间段结束')
    RESULT_CHOICE = ((0, '未运行'), (1, '运行中'), (2, '运行结束'), (3, '运行异常'))
    run_status = models.CharField(max_length=50, verbose_name='运行状态', default=0, choices=RESULT_CHOICE)
    rebotList = models.TextField(default=None, verbose_name='群机器人')
    projectList = models.TextField(default=None, verbose_name='项目list')
    caseList = models.TextField(default=None, verbose_name='caselist')
    envList = models.TextField(default=None, verbose_name='环境列表')
    emailList = models.TextField(default=None, verbose_name='收件人邮箱列表')
    msLogList = models.TextField(default=None, verbose_name='微服务日志列表')
    bigDataList = models.TextField(default=None, verbose_name='大数据列表')
    dbList = models.TextField(default=None, verbose_name='数据库列表')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')
    project_id = models.IntegerField(default=None, null=True, verbose_name='项目id')
    cron = models.CharField(max_length=20,default=None, null=True, verbose_name='cron表达式')

    def __str__(self):
        return self.plan_name


class Report(models.Model):
    """
    报告
    """
    report_id = models.AutoField(primary_key=True, null=False)
    report_name = models.CharField(max_length=255, verbose_name='报告名字')
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    case_num = models.IntegerField(null=True, verbose_name='用例运行数')
    pass_num = models.IntegerField(null=True, verbose_name='成功数')
    fail_num = models.IntegerField(null=True, verbose_name='失败数')
    error_num = models.IntegerField(null=True, verbose_name='错误数')
    api_total_nums = models.IntegerField(null=True, verbose_name='执行大数据api是否存在总数')
    pass_api_total_nums = models.IntegerField(null=True, default=None, verbose_name='大数据总api通过数')
    fail_api_total_nums = models.IntegerField(null=True, default=None, verbose_name='大数据总api失败数')
    error_api_total_nums = models.IntegerField(null=True, default=None, verbose_name='大数据总api错误数')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.report_name


class CaseTestResult(models.Model):
    """
    任务各个用例执行结果
    """
    case_result_id = models.AutoField(primary_key=True, verbose_name='执行结果id')
    case = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name='测试用例ID')
    case_name = models.CharField(max_length=50, default=None)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, verbose_name='报告ID')
    responseData = models.TextField(blank=True, null=True, verbose_name='实际返回内容')
    RESULT_CHOICE = (('Pass', '成功'), ('Fail', '失败'), ('Error', '错误'))
    result = models.CharField(max_length=50, verbose_name='任务执行结果', choices=RESULT_CHOICE)
    mslog_name = models.CharField(max_length=100, default=None, null=True, verbose_name='错误日志名字')
    mslog_path = models.CharField(max_length=200, default=None, null=True, verbose_name='错误日志路径')
    assertParamResult = models.TextField(blank=True, null=True, verbose_name='断言结果')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    request_body = models.TextField(blank=True, null=True, default=None, verbose_name='请求data')
    request_header = models.TextField(blank=True, null=True, default=None, verbose_name='请求header')
    take_up_time = models.CharField(max_length=50, default=None, null=True, verbose_name='运行时间')


class TaskHistory(models.Model):
    """
    定时任务执行历史表
    """
    task_id = models.AutoField(primary_key=True, verbose_name="历史执行id")
    project_id = models.IntegerField(null=True, verbose_name='项目id')
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE, verbose_name='外键plan_id')
    start_time = models.CharField(max_length=100, null=True, verbose_name='开始时间')
    end_time = models.CharField(max_length=100, null=True, verbose_name='结束时间')
    run_time = models.CharField(max_length=100, null=True, verbose_name='运行耗时')
    run_result = models.CharField(max_length=10, null=True, verbose_name='运行结果')
    run_people = models.CharField(max_length=100, default='sys', verbose_name='运行人')
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    update_person = models.CharField(max_length=50, null=True, verbose_name='更新人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')

    class Meta:
        db_table = 'plan_run_history'


class Jobs(models.Model):
    """
    脚本管理
    """
    job_id = models.AutoField(primary_key=True, verbose_name='jobID')
    job_name = models.CharField(max_length=200, verbose_name='脚本名称')
    description = models.CharField(max_length=200, null=True, verbose_name='脚本描述')
    file_name = models.CharField(max_length=200, verbose_name='文件名称')
    save_file_name = models.CharField(max_length=200, default=None, verbose_name='实际保存的文件名字')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')


class Env(models.Model):
    """
    环境管理
    """
    env_id = models.AutoField(primary_key=True, verbose_name='环境主键')
    env_name = models.CharField(max_length=200, verbose_name='环境名字')
    env_url = models.CharField(max_length=200, verbose_name='环境地址')
    ENV_TYPE = ((0, '测试'), (1, '开发'), (2, '预发'), (3, '线上'))
    env_type = models.IntegerField(default=0, verbose_name='环境类型', choices=ENV_TYPE)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')


class Email(models.Model):
    """
    邮箱管理
    """
    email_id = models.AutoField(primary_key=True, verbose_name='邮箱主键')
    email_name = models.CharField(max_length=200, verbose_name='邮箱名字')
    EMAIL_TYPE = ((0, '收件人'), (1, '发件人'))
    email_type = models.CharField(default=0, max_length=50, verbose_name='邮箱类型', choices=EMAIL_TYPE)
    email_address = models.CharField(max_length=200, verbose_name='邮箱地址')
    email_password = models.CharField(max_length=200, default=None, null=True, verbose_name='邮箱密码')
    smtp_address = models.CharField(max_length=200, default=None, null=True, verbose_name='smtp地址')
    smtp_port = models.CharField(max_length=20, default=None, null=True, verbose_name='smtp端口')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')


class MSLog(models.Model):
    """
    微服务日志
    """
    ms_id = models.AutoField(primary_key=True, verbose_name='微服务日志主键')
    project = models.ForeignKey('Project', null=True, on_delete=models.CASCADE)
    module = models.ForeignKey('Module', null=True, on_delete=models.CASCADE)
    ms_name = models.CharField(max_length=200, verbose_name='微服务名字')
    ms_ip = models.CharField(max_length=50, verbose_name='微服务ip')
    ms_port = models.CharField(max_length=10, verbose_name='微服务port')
    ms_user = models.CharField(max_length=50, verbose_name='用户名')
    ms_password = models.CharField(max_length=50, verbose_name='密码')
    ms_log_list = models.TextField(blank=True, null=True, verbose_name='微服务日志列表')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')


class Database(models.Model):
    db_id = models.AutoField(primary_key=True, verbose_name='数据库主键')
    db_name = models.CharField(max_length=200, verbose_name='数据库名字')
    connect_name = models.CharField(max_length=200, default=None, verbose_name='连接名称')
    db_host = models.CharField(max_length=50, verbose_name='数据库host')
    db_port = models.CharField(max_length=50, verbose_name='数据库端口号')
    db_user = models.CharField(max_length=50, verbose_name='数据库用户名')
    db_passwd = models.CharField(max_length=50, verbose_name='数据库密码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')
    db_type = models.CharField(max_length=50, verbose_name='数据库类型')


class Params(models.Model):
    param_id = models.AutoField(primary_key=True, verbose_name='参数主键')
    param_name = models.CharField(max_length=200, verbose_name='参数名字')
    Param_Type = ((0, '顺序字典'), (1, '随机字典'), (2, '最新月份'), (3, '最新年份'), (4, '最新日期'), (5, '昨日日期'))
    param_type = models.IntegerField(choices=Param_Type, null=True, default=None)
    description = models.CharField(max_length=200, null=True, verbose_name='用例描述')
    param_list = models.TextField(default=None, null=True, verbose_name='字典集')
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    update_person = models.CharField(max_length=50, null=True, verbose_name='更新人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')


class Robot(models.Model):
    robot_id = models.AutoField(primary_key=True, verbose_name='主键')
    group_name = models.CharField(max_length=200, default=None, verbose_name='组名称')
    p_id = models.IntegerField(null=True, default=None, verbose_name='父id')
    Type = ((1, '组'), (2, '机器人'))
    type = models.IntegerField(choices=Type, null=True, default=None)
    robot_name = models.CharField(max_length=200, null=True, verbose_name='机器人名称')
    keywordList = models.TextField(default=None, null=True, verbose_name='关键词列表')
    web_hook = models.TextField(default=None, null=True, verbose_name='web_hook')
    creator = models.CharField(max_length=50, null=True, verbose_name='创建人')
    update_person = models.CharField(max_length=50, null=True, verbose_name='更新人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.CharField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')

    class Meta:
        db_table = 'config_robot'
