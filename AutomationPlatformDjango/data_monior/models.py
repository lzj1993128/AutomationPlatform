from django.db import models
import django.utils.timezone as timezone
import datetime

IS_DELETE = ((0, False), (1, True))


class Datamonior(models.Model):
    project = models.CharField(max_length=100, null=True, verbose_name='所属项目')
    table = models.CharField(max_length=100, null=True, verbose_name='表名')
    rule_sql = models.TextField(null=True, verbose_name='规则sql')
    check_way = models.CharField(max_length=100, null=True, verbose_name='校验方式')
    check_type = models.CharField(max_length=100, null=True, verbose_name='校验类型')
    desired_value = models.IntegerField(null=True, verbose_name='期望值')
    compare_way = models.CharField(max_length=100, null=True, verbose_name='比较方式')
    rule_name = models.CharField(max_length=100, null=True, verbose_name='规则名')
    describe = models.CharField(max_length=100, null=True, verbose_name='描述')
    person = models.CharField(max_length=100, null=True, verbose_name='责任人')
    person_phone = models.CharField(max_length=100, null=True, verbose_name='责任人手机号')
    is_delete = models.BooleanField(choices=IS_DELETE, default=0, max_length=20, verbose_name='是否删除')
    is_enable = models.BooleanField(default=0, verbose_name='是否启用')
    creat_time = models.CharField(max_length=100, null=True, verbose_name='创建时间')
    update_time = models.CharField(max_length=100, null=True, verbose_name='更新时间')
    level = models.CharField(null=True, max_length=100, verbose_name='规则等级')


class Datamonior_History(models.Model):
    rule_id = models.CharField(max_length=100, null=True, verbose_name='规则id')
    status = models.CharField(max_length=100, null=True, verbose_name='状态')
    run_result = models.CharField(max_length=100, null=True, verbose_name='执行结果')
    run_date = models.CharField(max_length=100, null=True, verbose_name='执行日期')
    pt = models.CharField(max_length=100, null=True, verbose_name='分区时间')
    project = models.CharField(max_length=100, null=True, verbose_name='所属项目')
    table = models.CharField(max_length=100, null=True, verbose_name='表名')
    person = models.CharField(max_length=100, null=True, verbose_name='责任人')
    person_phone = models.CharField(max_length=100, null=True, verbose_name='责任人手机号')
    check_type = models.CharField(max_length=100, null=True, verbose_name='校验类型')
    rule_name = models.CharField(max_length=100, null=True, verbose_name='规则名')
    rule_sql = models.TextField(null=True, verbose_name='规则sql')
    check_way = models.CharField(max_length=100, null=True, verbose_name='校验方式')
    compare_way = models.CharField(max_length=100, null=True, verbose_name='比较方式')
    desired_value = models.IntegerField(null=True, verbose_name='期望值')
    level = models.CharField(null=True, max_length=100, verbose_name='规则等级')


class run_log(models.Model):
    run_date = models.CharField(max_length=100, null=True, verbose_name='运行日期')
    st_time = models.CharField(max_length=100, null=True, verbose_name='开始时间')
    end_time = models.CharField(max_length=100, null=True, verbose_name='结束时间')
    run_time = models.CharField(max_length=100, null=True, verbose_name='运行耗时')
    job_name = models.CharField(max_length=100, null=True, verbose_name='任务名称')
    res = models.TextField(null=True, verbose_name='运行状态')


class dataworks_alltables_rule(models.Model):
    table_schema = models.CharField(max_length=100, null=True, verbose_name='表空间')
    table_name = models.CharField(max_length=100, null=True, verbose_name='表名')
    owner_name = models.CharField(max_length=100, null=True, verbose_name='创建者中文名')
    accountname = models.CharField(max_length=100, null=True, verbose_name='规则创建者')
    create_owner_name = models.CharField(max_length=100, null=True, verbose_name='表创建者中文名')
    table_comment = models.CharField(max_length=255, null=True, verbose_name='表备注')
    table_id = models.CharField(max_length=100, null=True, verbose_name='表id')
    status = models.CharField(max_length=100, null=True, verbose_name='接口调用结果:0成功，1报错，2未配置数据预警')
    description = models.CharField(max_length=100, null=True, verbose_name='接口结果描述：0成功，1报错，2未配置数据预警')
    data_model = models.CharField(max_length=100, null=True, verbose_name='数仓分层')
    create_time = models.CharField(max_length=100, null=True, verbose_name='创建时间')
    project = models.CharField(max_length=100, null=True, verbose_name='所属项目')
    accountnameid = models.CharField(max_length=100, null=True, verbose_name='责任人工号')


class dataworks_alltables_rule_result(models.Model):
    table_schema = models.CharField(max_length=100, null=True, verbose_name='表空间')
    project = models.CharField(max_length=100, null=True, verbose_name='所属项目')
    table_name = models.CharField(max_length=100, null=True, verbose_name='表名')
    data_model = models.CharField(max_length=100, null=True, verbose_name='数仓分层')
    owner_name = models.CharField(max_length=100, null=True, verbose_name='创建者id')
    accountname = models.CharField(max_length=100, null=True, verbose_name='规则创建者')
    create_owner_name = models.CharField(max_length=100, null=True, verbose_name='表创建者中文名')
    table_comment = models.CharField(max_length=255, null=True, verbose_name='表备注')
    table_id = models.CharField(max_length=100, null=True, verbose_name='表id')
    status = models.CharField(max_length=100, null=True, verbose_name='接口调用结果:0成功，1报错，2未配置数据预警')
    description = models.CharField(max_length=100, null=True, verbose_name='接口结果描述：0成功，1报错，2未配置数据预警')
    ruleid = models.CharField(max_length=100, null=True, verbose_name='规则id')
    rulename = models.CharField(max_length=100, null=True, verbose_name='规则名字')
    checkresult = models.CharField(max_length=100, null=True,
                                   verbose_name='校验结果 0：正常 1：橙色告警 2：红色告警 3:规则未配置 4：接口异常 -2：异常')
    runtime = models.CharField(max_length=100, null=True, verbose_name='运行时间')
    bizdate = models.CharField(max_length=100, null=True, verbose_name='分区日期')
    job_run_date = models.CharField(max_length=100, null=True, verbose_name='接口调用时间')
    check_type = models.CharField(max_length=100, null=True, verbose_name='校验类型')
    error_num = models.CharField(max_length=100, null=True, verbose_name='校验结果')
    handle_status = models.CharField(max_length=100, null=True, verbose_name='处理状态，1：已处理 0：待处理')
    over_time = models.CharField(max_length=100, null=True, verbose_name='预计处理时间')
    accountnameid = models.CharField(max_length=100, null=True, verbose_name='责任人工号')
    resontype = models.CharField(max_length=100, null=True, verbose_name='问题类型')
    resontypedes = models.CharField(max_length=100, null=True, verbose_name='问题类型中文')


class dataworks_rule_handle(models.Model):
    ruleid = models.CharField(max_length=100, null=True, verbose_name='规则id')
    reson = models.CharField(max_length=100, null=True, verbose_name='产生原因')
    person = models.CharField(max_length=100, null=True, verbose_name='处理人')
    conduct = models.CharField(max_length=100, null=True, verbose_name='处理方式')
    conduct_time = models.CharField(max_length=100, null=True, verbose_name='处理时间')
    over_time = models.CharField(max_length=100, null=True, verbose_name='预计完成时间')
    finish_status = models.CharField(default=0, null=True, max_length=100, verbose_name='完成状态，0：处理中 1：成功 2：失败')
    conduct_id = models.CharField(max_length=100, null=True, verbose_name='处理id')
    resontype = models.CharField(max_length=100, null=True, verbose_name='问题类型')
    resontypedes = models.CharField(max_length=100, null=True, verbose_name='问题类型中文')


class dataExploration_Project(models.Model):
    Project = models.CharField(max_length=100, null=True, verbose_name='项目名称')
    Project_id = models.CharField(max_length=100, null=True, verbose_name='项目id')
    IterationName = models.CharField(max_length=100, null=True, verbose_name='迭代名称')
    State = models.IntegerField(null=True, verbose_name='环境code')
    Statedes = models.CharField(max_length=100, null=True, verbose_name='状态中文名')
    DevPersons = models.CharField(max_length=100, null=True, verbose_name='开发负责人')
    TestPersons = models.CharField(max_length=100, null=True, verbose_name='测试负责人')
    ScheduleTestTime = models.CharField(max_length=100, null=True, verbose_name='计划提测时间')
    PlannedReleaseDate = models.CharField(max_length=100, null=True, verbose_name='计划发布时间')
    modifyDate = models.DateTimeField(default=timezone.now, verbose_name='最后修改时间')
    createDate = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    is_delete = models.IntegerField(null=True, default=0, verbose_name='是否删除')


class dataExploration_RuleTable(models.Model):
    proId = models.ForeignKey('dataExploration_Project', on_delete=models.CASCADE)
    source = models.CharField(max_length=100, null=True, verbose_name='数据源')
    tableschema = models.CharField(max_length=100, null=True, verbose_name='domain')
    tableName = models.CharField(max_length=100, null=True, verbose_name='表名')
    tableChName = models.CharField(max_length=100, null=True, verbose_name='中文名')
    majorkey = models.TextField(null=True, verbose_name='主键')
    where = models.TextField(null=True, verbose_name='查询条件')
    # LastProbeTime = models.DateTimeField(null=True, verbose_name='最近探查时间')
    LastProbeTime = models.CharField(max_length=100, null=True,verbose_name='最近探查时间')
    columnsInfo = models.TextField(null=True, verbose_name='字段信息')
    status = models.IntegerField(null=True, default=0, verbose_name='状态')
    statusdes = models.CharField(max_length=100, null=True, default='未探查', verbose_name='状态解释0：未探查 1：成功 2：失败 3：探查中')
    createPersons = models.CharField(max_length=100, null=True, verbose_name='创建人')
    modifyDate = models.DateTimeField(default=timezone.now, verbose_name='最后修改时间')
    createDate = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    is_delete = models.IntegerField(null=True, default=0, verbose_name='是否删除')


class dataExploration_TableHistory(models.Model):
    tableId = models.ForeignKey('dataExploration_RuleTable', on_delete=models.CASCADE)
    taskId = models.CharField(max_length=100, null=True, verbose_name='任务ID')
    source = models.CharField(max_length=100, null=True, verbose_name='数据源')
    table = models.CharField(max_length=100, null=True, verbose_name='表名')
    where = models.TextField(null=True, verbose_name='查询条件')
    table_comment = models.CharField(max_length=100, null=True, verbose_name='表中文名')
    environment = models.IntegerField(null=True, verbose_name='环境code 0:线上 1:开发')
    environmentdes = models.CharField(max_length=100, null=True, verbose_name='环境中文名')
    owner = models.CharField(max_length=100, null=True, verbose_name='表创建者')
    createTime = models.CharField(max_length=100, null=True, verbose_name='表创建时间')
    tableallnum = models.CharField(max_length=100, null=True, verbose_name='表总数')
    repeatResult = models.IntegerField(null=True, verbose_name='重复数据数')
    repeatDetailsSql = models.TextField(null=True, verbose_name='重复数据sql')
    pkRepeatResult = models.IntegerField(null=True, verbose_name='主键重复数')
    pkDetailsSql = models.TextField(null=True, verbose_name='主键重复sql')
    dataSize = models.CharField(max_length=100, null=True, verbose_name='表数据大小')
    lifeCycle = models.IntegerField(null=True, verbose_name='表生命周期')
    # probeTime = models.DateTimeField(null=True, verbose_name='探查时间')
    probeTime = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 verbose_name='探查时间')
    majorkey = models.TextField(null=True, verbose_name='主键字段')
    runTime = models.CharField(max_length=100, null=True, verbose_name='运行时间')
    # modifyDate = models.DateTimeField(default=timezone.now, verbose_name='最后修改时间')
    # createDate = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    modifyDate = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  verbose_name='最后修改时间')
    createDate = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  verbose_name='创建时间')
    comment = models.TextField(null=True, verbose_name='备注')
    status = models.IntegerField(null=True, default=0, verbose_name='最新状态')
    statusdes = models.CharField(max_length=100, null=True, default='未运行',
                                 verbose_name='状态解释0：未运行 1：成功 2：失败 3：运行中 4：报错')


class dataExploration_TableColumnsHistory(models.Model):
    # task = models.ForeignKey('dataExploration_TableHistory', on_delete=models.CASCADE)
    taskId = models.CharField(max_length=100, null=True, verbose_name='任务ID')
    name = models.CharField(max_length=100, null=True, verbose_name='字段名')
    comment = models.CharField(max_length=100, null=True, verbose_name='字段中文名')
    type = models.CharField(max_length=100, null=True, verbose_name='字段类型')
    typedes = models.CharField(max_length=100, null=True, verbose_name='字段类型中文名')
    columnnull = models.IntegerField(null=True, verbose_name='空值数')
    cnt_distinct = models.IntegerField(null=True, verbose_name='唯一值数')
    max_l = models.IntegerField(null=True, verbose_name='最大长度')
    min_l = models.IntegerField(null=True, verbose_name='最小长度')
    max_v = models.BigIntegerField(null=True, verbose_name='最大值')
    min_v = models.BigIntegerField(null=True, verbose_name='最小值')
    avg_v = models.BigIntegerField(null=True, verbose_name='平均值')
    distinct_v = models.TextField(null=True, verbose_name='枚举值')
    sql = models.TextField(null=True, verbose_name='查询sql')


class dataExploration_TableDynamicheader(models.Model):
    type = models.CharField(max_length=100, null=True, verbose_name='字段类型')
    column = models.CharField(max_length=100, null=True, verbose_name='字段名')
    column_comment = models.CharField(max_length=100, null=True, verbose_name='字段中文名')


class dataExploration_TestCase(models.Model):
    # task = models.ForeignKey('dataExploration_TableHistory', on_delete=models.CASCADE)
    proId = models.ForeignKey('dataExploration_Project', on_delete=models.CASCADE)
    CaseName = models.CharField(max_length=100, null=True, verbose_name='用例名称')
    CaseLevel = models.CharField(max_length=100, null=True, verbose_name='用例等级')
    CaseType = models.CharField(max_length=100, null=True, verbose_name='用例类型')
    # column = models.TextField(null=True, verbose_name='维度字段')
    columnRuleList = models.TextField(null=True, verbose_name='字段规则')
    person = models.CharField(max_length=100, null=True, verbose_name='创建者')
    CaseDes = models.TextField(null=True, verbose_name='用例描述')
    sql = models.TextField(null=True, verbose_name='查询sql')
    status = models.IntegerField(null=True, default=0, verbose_name='最新状态')
    statusdes = models.CharField(max_length=100, null=True, default='未运行',
                                 verbose_name='状态解释0：未运行 1：成功 2：失败 3：运行中 4：报错')
    LastProbeTime = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                     verbose_name='最近探查时间')
    is_delete = models.IntegerField(null=True, default=0, verbose_name='删除状态')
    # modifyDate = models.DateTimeField(default=timezone.now, verbose_name='最后修改时间')
    modifyDate = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  verbose_name='最后修改时间')
    # createDate = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    createDate = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  verbose_name='创建时间')


class dataExploration_TestCaseRunHistory(models.Model):
    # task = models.ForeignKey('dataExploration_TableHistory', on_delete=models.CASCADE)
    caseId = models.ForeignKey('dataExploration_TestCase', on_delete=models.CASCADE)
    CaseName = models.CharField(max_length=100, null=True, verbose_name='用例名称')
    caseResult = models.TextField(null=True, verbose_name='用例结果')
    sql = models.TextField(null=True, verbose_name='查询sql')
    status = models.IntegerField(null=True, default=0, verbose_name='状态')
    statusdes = models.CharField(max_length=100, null=True, default='未运行',
                                 verbose_name='状态解释0：未运行 1：成功 2：失败 3：运行中 4：报错')
    # starttime = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    # endtime = models.DateTimeField(default=timezone.now, verbose_name='结束时间')
    runtime = models.CharField(max_length=100, null=True, verbose_name='耗时')
    starttime = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 verbose_name='开始时间')
    # createDate = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    endtime = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                               verbose_name='结束时间')
    comment = models.TextField(null=True, verbose_name='备注')


class dataExploration_QuestionInfo(models.Model):
    # task = models.ForeignKey('dataExploration_TableHistory', on_delete=models.CASCADE)
    questionID = models.CharField(max_length=100, null=True, verbose_name='问题ID')
    prj = models.ForeignKey('api.Project', on_delete=models.CASCADE)
    prj_name = models.CharField(max_length=100, null=True, verbose_name='项目名称')
    currentAssignmentID = models.IntegerField(null=True, verbose_name='被指派人工号')
    currentAssignment = models.CharField(max_length=100, null=True, verbose_name='被指派人名字')
    currentAssignmentPhone = models.CharField(max_length=20, null=True, verbose_name='被指派人手机号')
    currentAssignmentTime = models.CharField(max_length=100,
                                             default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                             verbose_name='当前指派时间')
    planSolveTime = models.CharField(max_length=100, null=True,
                                     verbose_name='计划解决时间')
    questionTitle = models.TextField(null=True, verbose_name='问题标题')
    repeatSteps = models.TextField(null=True, verbose_name='重现步骤')
    createDate = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  verbose_name='创建时间')
    status = models.IntegerField(null=True, default=0, verbose_name='问题状态')
    statusdes = models.CharField(max_length=100, null=True, default='待解决', verbose_name='问题状态中文名0待解决 1解决中 2已解决')
    is_delete = models.IntegerField(null=True, default=0, verbose_name='删除状态')
    questionChannels = models.CharField(max_length=100, null=True, verbose_name='问题渠道：APP端，门店端')
    questionType = models.CharField(max_length=100, null=True, verbose_name='问题模块：当前里程模块，下次保养时间模块，处理计划模块，车况明细模块，门店提醒问题')
    Type = models.CharField(max_length=100, null=True, verbose_name='类型')

    # Typedes = models.CharField(max_length=100,default='线上问题跟踪', null=True,  verbose_name='类型：0线上问题跟踪、1指标跟踪')
    # closeTime = models.CharField(max_length=100, null=True, verbose_name='关闭时间')
    class Meta:
        indexes = [models.Index(fields=['questionID']), ]


class dataExploration_QuestionHandleHistory(models.Model):
    # task = models.ForeignKey('dataExploration_TableHistory', on_delete=models.CASCADE)
    questionID = models.CharField(max_length=100, null=True, verbose_name='问题ID')
    handleType = models.IntegerField(null=True, verbose_name='类型：0 创建 1 指派 2 解决')
    handlerID = models.IntegerField(null=True, verbose_name='指派人ID')
    handler = models.CharField(max_length=100, null=True, verbose_name='指派人名字')
    currentAssignmentID = models.IntegerField(null=True, verbose_name='被指派人工号')
    currentAssignment = models.CharField(max_length=100, null=True, verbose_name='被指派人名字')
    currentAssignmentPhone = models.CharField(max_length=20, null=True, verbose_name='被指派人手机号')
    createDate = models.CharField(max_length=100, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  verbose_name='创建时间')
    solveTime = models.CharField(max_length=100, null=True, verbose_name='解决时间')
    questionBelong = models.CharField(max_length=100, null=True, verbose_name='问题归属')
    comment = models.TextField(null=True, verbose_name='备注')
    Type = models.CharField(max_length=100, null=True, verbose_name='问题类型')

    class Meta:
        indexes = [models.Index(fields=['questionID']), ]
    # planSolveTime = models.DateTimeField(default=timezone.now, verbose_name='计划解决时间')
    # questionTitle = models.CharField(max_length=100, null=True, verbose_name='问题标题')
    # repeatSteps = models.TextField(null=True, verbose_name='重现步骤')
    # createDate = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    # status = models.IntegerField(null=True, default=0, verbose_name='问题状态')
    # statusdes = models.CharField(max_length=100, null=True, default='解决中', verbose_name='问题状态中文名')
    # is_delete = models.IntegerField(null=True, default=0, verbose_name='删除状态')
    # closeTime = models.DateTimeField(null=True, verbose_name='关闭时间')
# Create your models here.
