# -*- coding: utf-8 -*-
import datetime
import json
import logging
import re

from api.exception.case.CaseServiceException import RequestJsonError, RequestBodyError, ConnectSqlError
from api.models import Case, ApiResult, Interface, CaseResult, Env, Database, User, Params
from api.service.param.ParamService import ParamService
from common.base.BaseService import BaseService
# from utils.Dubbo import Dubbo, GetDubboService
from utils.SignUtil import signByMd5

logger = logging.getLogger('log')


class CaseService(BaseService):
    def __init__(self, stepData=None, envData=None, case_id=None, case_type=None):
        """
        数据初始化
        :param stepData: 步骤数据
        :param envData: 环境数据
        """
        self.case_run = []
        if envData is not None:
            if isinstance(envData, str):
                self.envData = eval(envData)
            else:
                self.envData = envData
        if case_id and case_type:
            self.case_id = case_id
            self.step_list = stepData
        elif case_id and case_type is None:
            self.case_id = case_id
            self.step_list = json.loads(Case.objects.get(case_id=case_id).step_info)
        else:
            self.case_id = None
            if stepData:
                if isinstance(stepData, str):
                    self.step_list = json.loads(stepData)
                else:
                    self.step_list = stepData

    def getEnvUrl(self, project_id):
        """
        返回各个接口所需要的环境地址，根据项目id判断
        :param project_id: 传进一个接口储存的项目id参数
        :return: 项目url
        """
        try:
            urlForm = dict()
            url = ''
            zk_url = ''
            env_type = ''
            for env in self.envData:
                prj_id = env.get('selectEvnPrject')
                other_url = env.get('other_url')
                # 专门为dubbo加的判断，获取项目zk服务器地址
                zk_url = env.get('zk_database')
                env_type = Env.objects.get(env_id=env.get('selectEvnUrl')).env_type
                if project_id == prj_id:
                    if other_url == '':
                        # selectEvnUrl其实是env_id
                        env_id = int(env.get('selectEvnUrl'))
                        url = Env.objects.get(env_id=env_id).env_url
                    else:
                        url = other_url
            urlForm['httpUrl'] = url
            urlForm['zkUrl'] = zk_url
            urlForm['envType'] = env_type
            logger.info('项目请求地址为:{}'.format(urlForm))
            return urlForm
        except Exception as e:
            logger.error(e)

    def getValue(self, value, interfaceORCaseId=None, id=None, selectBodyIndexValue=None):
        """
        确认$符号，方便根据这个查找字段,返回字段的值，
        $要取得字段$接口或者用例id$下标$类型是接口还是用例
        :param value: value值
        :param interfaceORCaseId: 需要获取的是接口id，还是用例id
        :param id: id号是多少
        :param selectBodyIndexValue:取值的下标
        :return:
        """
        if isinstance(value, str):
            if '$' in value:
                logger.info('需要处理的字段值是{}'.format(value))
                realValue = value.split('$')[1]
                try:
                    valueId = int(value.split('$')[2])
                    valueId = id if valueId == '' else valueId
                except Exception as e:
                    logger.error('说明不存在需要修改的id，异常信息{}'.format(e))
                    valueId = id
                try:
                    selectBodyIndex = int(value.split('$')[3])
                    selectBodyIndex = selectBodyIndexValue if selectBodyIndex == '' else selectBodyIndex
                except Exception as e:
                    logger.error('说明不需要修改的下标，异常信息{}'.format(e))
                    selectBodyIndex = selectBodyIndexValue
                logger.info('$符号存在，获取需要取的关联值{}'.format(realValue))
                try:
                    interfaceORCaseId = int(value.split('$')[4])
                except Exception as e:
                    logger.error('说明不需要修改的获取接口的类型，异常信息{}'.format(e))
                if interfaceORCaseId == 0:
                    logger.info('依赖的是接口id:{}的结果'.format(valueId))
                    apiIdResult = eval(ApiResult.objects.get(api_id=valueId).content)
                elif interfaceORCaseId == 1:
                    logger.info('依赖的是用例id:{}的结果'.format(valueId))
                    apiIdResult = eval(CaseResult.objects.get(case_id=valueId).content)
                else:
                    logger.info('依赖的是公共前置用例id{}的结果'.format(id))
                    case = CaseResult.objects.filter(case_id=id)
                    if case.count() == 0:
                        logger.info('说明没有运行过这个公共用例，需要先运行下')
                        step_info = eval(Case.objects.get(case_id=id).step_info)
                        self.runStepInfo(step_info, id)
                        apiIdResult = eval(CaseResult.objects.get(case_id=id).content)
                    else:
                        logger.info('说明已经运行过这个公共用例，判断运行的时间')
                        timeNow = datetime.datetime.now().strftime('%Y-%m-%d')
                        logger.info('获取现在的时间{}'.format(timeNow))
                        update_time = CaseResult.objects.get(case_id=id).update_time
                        update_time_fomat = update_time.strftime('%Y-%m-%d')
                        logger.info('获取最近执行这个用例的时间{}'.format(update_time_fomat))
                        #  判断这个公共用例是否需要再运行一次逻辑，一天确保只运行一次
                        if timeNow == update_time_fomat:
                            logger.info("说明今天已经执行过这个用例，不需要再次执行")
                            apiIdResult = eval(CaseResult.objects.get(case_id=id).content)
                        else:
                            logger.info("说明今天没有执行过这个用例，需要执行一次")
                            step_info = json.loads(Case.objects.get(case_id=id).step_info)
                            self.runStepInfo(step_info, id)
                            apiIdResult = eval(CaseResult.objects.get(case_id=id).content)
                logger.info('查询到的结果是{}'.format(apiIdResult))
                result = self.get_target_value(realValue, apiIdResult, [])[selectBodyIndex]
                value = self.changeType(realValue, result)
        return value

    def runStepInfo(self, stepInfoList, case_id):
        """
        提取前置用例和取公共的前置用例步骤运行
        :param stepInfoList:步骤列表
        :param case_id:用例id
        :return:
        """
        for step in stepInfoList:
            api_id = step.get('api_id')
            project_id = Interface.objects.get(api_id=api_id).project_id
            if step.get('request_method') == 'dubbo':
                logger.info('属于dubbo请求')
                result = self.dubboStep(step, case_id)

            else:
                logger.info('属于http请求')
                result = self.handleDataDriven(step, project_id, case_id)
            #  将单个用例结果添加到完整的用例中
            self.case_run.append(result)

    def analyzeRequestCaseIdListData(self, caseIdList):
        """
        分析用例关联，先执行前置关联用例，存储用例执行结果
        :param caseIdList:
        :return:
        """
        try:
            if not isinstance(caseIdList, list):
                caseIdList = eval(caseIdList)
        except TypeError as e:
            logger.error('前置条件caseIdList eval异常{}'.format(e))
            caseIdList = caseIdList
        if len(caseIdList) != 0:
            logger.info('前置条件用例不为空，执行前置条件用例')
            for case in caseIdList:
                case_id = case.get('case_id')
                step_info = eval(Case.objects.get(case_id=case_id).step_info)
                self.runStepInfo(step_info, case_id)
        pass

    def changeValue(self, value, typeValue, queryDict=None):
        """
        将前端body值根据类型进行转化，请求服务端接口
        :param value:值
        :param typeValue:需要转换的类型
        :param queryDict:数据驱动逻辑 字段
        :return:
        """
        try:
            logger.info('将{}进行类型转换'.format(value))
            if typeValue == 'str':
                logger.info('检测到值是str类型，转换成str类型')
                value = str(value)
            elif typeValue == 'int':
                logger.info('检测到值是整数类型，转换成int类型')
                value = int(value)
            elif typeValue == 'float':
                logger.info('检测到值是浮点类型，转换成float类型')
                value = float(value)
            elif typeValue == 'dict':
                logger.info('检测到值是字典类型，转换成字典类型')
                value = json.loads(value) if value else {}
            elif typeValue == 'boolean':
                logger.info('检测到值是布尔类型，转换成布尔类型')
                value = True if value == 'true' or value == 'True' else False
            elif typeValue == 'now':
                logger.info('检测到值是now，返回value为当前时间')
                value = self.get_now()
            elif typeValue == 'null':
                logger.info('检测到类型为空，返回None')
                value = None
            elif typeValue == '空字符串':
                logger.info('检测到是空字符串类型')
                value = ''
            elif typeValue == 'ac':
                logger.info('检测到自动获取ac')
                value = User.objects.get(user_id=1).ac_token
            elif typeValue == 'dataDrive':
                logger.info('获取到是数据驱动')
                pattern = re.compile(r'\${1}\w{1,20}')
                valueList = pattern.findall(value)
                # 获取到的是这样的列表['$date']
                for v in valueList:
                    queryValue = v.split('$')[1]
                    if queryValue in queryDict.keys():
                        value = value.replace(v, queryDict[queryValue])
                    else:
                        continue
                try:
                    value = json.loads(value)
                except Exception as e:
                    logger.error('数据驱动异常')
                    value = value
                return value
            else:
                value = eval(value)
            logger.info('打印已经转换好的值:{}'.format(value))
            return value
        except Exception as e:
            logger.error('值类型转换异常：{}'.format(e))
            return value

    def analyzeRequestRequestJson(self, requestJson):
        """
        处理json请求
        :param requestJson:需要处理的请求参数
        :return:
        """
        requestJson = re.sub('\s+', '', requestJson).strip()
        logger.info('打印需要处理的数据：{}'.format(requestJson))
        try:
            requestValue = json.loads(requestJson)
            requestValue = self.handleRequestJson(requestValue)
            logger.info('请求的json数据{}'.format(requestValue))
            return requestValue
        except Exception as e:
            logger.error('处理数据json数据异常')
            raise RequestJsonError(e)

    def reRequestJson(self, requestJson):
        """
        通过re规则查找需要变化得字段 正则匹配如$book$17$1$0
        编辑时间：20201214
        $book:要取的参数
        $17：接口id或者用例id
        $1：用例  0 ：接口  2：公共接口 3：数据驱动（目前还用不到）
        $0:表示取的下标记
        :return:
        """
        # json串适合这个规则
        patternOne = re.compile(r'\${1}?.{1,20}\${1}?\d*?\${1}?\d*?\${1}?\d{1}?')
        valueListOne = patternOne.findall(requestJson)
        # 只是一个字符串 比如  $book
        patternTwo = re.compile(r'^\${1}?.{1,20}?$')
        valueListTwo = patternTwo.findall(requestJson)
        return valueListOne, valueListTwo

    def getSessionIdAndSecret(self, envType):
        """
        通过envType判断，要获取哪个环境的session-id和Secret
        :param envType:
        :return:
        """
        if envType == 0:
            logger.info('获取测试主干环境的session-id和secret')
            url = 'https://test-i0-superapiplus.carzone360.com/superapi/ps/getH5SessionAndSecret'
        elif envType == 1:
            logger.info('获取测试开发环境的session-id和secret')
            url = 'https://dev-i0-superapiplus.carzone360.com/superapi/ps/getH5SessionAndSecret'
        elif envType == 2:
            logger.info('获取测试预发环境的session-id和secret')
            url = 'https://pre-i0-superapiplus.carzone360.com/superapi/ps/getH5SessionAndSecret'
        else:
            # 线上不知道啥连接，20210701添加地址
            logger.info('获取测试线上环境的session-id和secret')
            url = 'https://api.ncarzone.com/superapi/ps/getH5SessionAndSecret'
        logger.info('请求地址{}'.format(url))
        result = self.requestApi('get', url=url)
        sessionId = self.get_target_value('session-id', result, [])[0]
        secret = self.get_target_value('secret', result, [])[0]
        signForm = {}
        signForm['sessionId'] = sessionId
        signForm['secret'] = secret
        logger.info('打印获取的session-id和secret：{}'.format(signForm))
        return signForm

    def handleRequestJson(self, requestJson):
        requestStr = json.dumps(requestJson, ensure_ascii=False)
        needChangeList = self.reRequestJson(requestStr)[0]
        needChangeListLen = len(needChangeList)
        if needChangeListLen != 0:
            for i in range(0, needChangeListLen):
                value = needChangeList[i]
                value = self.getValue(value)
                pattern = r'\${1}?.{1,20}\${1}?\d*?\${1}?\d*?\${1}?\d{1}?'
                requestStr = re.sub(pattern, value, requestStr, 1)
            requestJson = json.loads(requestStr)
        return requestJson

    def analyzeRequestListData(self, requestLists, queryDict):
        """
        处理请求的body list和header list
        :param requestLists:请求的完整列表
        :param queryDict:数据驱动逻辑字段，一个替换目标$date的实际值
        :return: header或者body
        """
        try:
            requestDict = {}
            if isinstance(requestLists, str):
                requestLists = eval(requestLists)
            for requestList in requestLists:
                sunParamList = requestList.get('sunParamList') if 'sunParamList' in requestList.keys() else []
                requestKey = requestList.get('key')
                requestType = requestList.get('type')
                if len(sunParamList) > 0:
                    resultDictT = {}
                    for param in sunParamList:
                        result = self.handleParam(param, queryDict)
                        for r in result.keys():
                            resultDictT[r] = result[r]
                    requestValue = self.changeValue(resultDictT, requestType, queryDict)
                    requestDict[requestKey] = requestValue
                else:
                    result = self.handleParam(requestList, queryDict)
                    requestDict[requestKey] = result[requestKey]
            return requestDict
        except Exception as e:
            logger.error('处理请求header或者body异常{}'.format(e))
            raise RequestBodyError(e)

    def handleParam(self, requestList, queryDict):
        requestDict = {}
        requestKey = requestList.get('key')
        requestValue = requestList.get('value')
        requestType = requestList.get('type')
        requestVauleChecked = requestList.get('vauleChecked')
        if not requestVauleChecked:
            logger.info('检测到vauleChecked 为False，说明不需要其他值代替')
            requestValue = self.changeValue(requestValue, requestType, queryDict)
            requestDict[requestKey] = requestValue
        else:
            logger.info('检测到vauleChecked 为True，说明需要其他值代替')
            #  interfaceORCaseId判断是apiID还是caseId
            interfaceORCaseId = int(requestList.get('interfaceORCaseId'))
            #  id是依赖的caseID或者apiID
            id = int(requestList.get('id'))
            #  selectBodyIndexValue选择对应id运行结果的下标
            selectIndexValue = int(requestList.get('selectIndexValue'))
            # 20210913重写运行逻辑,之前逻辑处理不了大于2层的嵌套传参数
            # 获取满足变化的值,返回一个满足改变的列表
            # 结果1：取值$book$17$1$0，检索到就替换
            resultOne = self.reRequestJson(requestValue)[0]
            if len(resultOne) != 0:
                for i in range(len(resultOne)):
                    value = resultOne[i]
                    value = self.getValue(value, interfaceORCaseId, id, selectIndexValue)
                    pattern = r'\${1}?.{1,20}\${1}?\d*?\${1}?\d*?\${1}?\d{1}?'
                    requestValue = re.sub(pattern, value, requestValue, 1)
            # 处理结果2：取值为$book,检索到就替换
            resultTwo = self.reRequestJson(requestValue)[1]
            if len(resultTwo) != 0:
                for j in range(len(resultTwo)):
                    value = resultTwo[j]
                    value = self.getValue(value, interfaceORCaseId, id, selectIndexValue)
                    pattern = re.compile(r'\${1}\w{1,20}')
                    requestValue = re.sub(pattern, value, requestValue, 1)
            requestDict[requestKey] = requestValue
        return requestDict

    def compareAssertValue(self, compareValue, val1, val2):
        """
        比较值
        :param compareValue:比较符号
        :param val1: 实际值
        :param val2: 预期值
        :return:布尔值
        """
        if compareValue == '=':
            logger.info('检测到比较类型为{}'.format(compareValue))
            compareResult = True if val1 == val2 else False
        elif compareValue == '>':
            logger.info('检测到比较类型为{}'.format(compareValue))
            compareResult = True if val1 > val2 else False
        elif compareValue == '<':
            logger.info('检测到比较类型为:{}'.format(compareValue))
            compareResult = True if val1 < val2 else False
        elif compareValue == '!=':
            logger.info('检测到比较类型为:{}'.format(compareValue))
            compareResult = True if val1 != val2 else False
        elif compareValue == 'in':
            logger.info('检测到比较类型为:{}'.format(compareValue))
            compareResult = True if val1 in val2 else False
        elif compareValue == '长度大于':
            logger.info('检测到比较类型为:{}'.format(compareValue))
            compareResult = True if len(val1) > val2 else False
        else:
            logger.info('没有检测到比较类型，默认为==')
            compareResult = True if val1 == val2 else False
        return compareResult

    def analyzeRequestAssertListData(self, assertList, requestHeaderData, requestBodyData, result=None, code=None,
                                     api_url=None, acTakeUpTime=None):
        """
        断言，返回一个断言结果dict
        :param assertList:断言的字段
        :param result:接口运行结果
        :param code:请求服务端网络判断层返回码
        :param api_url:请求的接口
        :return:将预期值按照填写的类型进行转换
        """
        assertResultList = []  # 对比参数结果列表
        assertResult = {'code': code, 'isPass': 'Pass', 'acTakeUpTime': acTakeUpTime, 'api': api_url, 'msg': '',
                        'assertResultList': [],
                        'requestHeaderData': requestHeaderData,
                        'requestBodyData': requestBodyData,
                        'result': result}
        if len(assertList) == 0:
            assertResult = {'code': code, 'isPass': 'Error', 'acTakeUpTime': acTakeUpTime, 'api': api_url,
                            'msg': '断言列表为空', 'assertResultList': [],
                            'requestHeaderData': requestHeaderData,
                            'requestBodyData': requestBodyData,
                            'result': result}
            return assertResult
        else:
            try:
                for asserts in assertList:
                    param = asserts.get('param')
                    expectedValue = asserts.get('expectedValue')
                    expectedType = asserts.get('type')
                    index = int(asserts.get('selectAssertIndexValue'))
                    compareValue = asserts.get('compareValue')
                    logger.info("判断下是否含有sql校验")
                    sql = asserts.get('sql') if 'sql' in asserts.keys() else None
                    db_id = int(asserts.get('db_id')) if 'db_id' in asserts.keys() and asserts.get(
                        'db_id') != '' else None
                    if sql and db_id:
                        logger.info("sql和bd_id都存在，执行sql")
                        expectedValue = self.searchSql(db_id, sql)
                    actualResult = self.get_target_value(param, result, [])
                    if len(actualResult) == 0:
                        # 实际结果没有获取到
                        logger.info('实际结果没有获取到')
                        msg = '断言字段【{}】在实际结果中没有找到，请确认参数是否填写正确'
                        logger.info(msg)
                        assertResult = {'code': code, 'isPass': 'Error', 'api': api_url, 'assertResultList': [],
                                        'msg': msg}
                        assertResultList.append(msg)
                        assertResult['assertResultList'] = assertResultList
                    else:
                        # 取到了实际结果，通过下标获取对应的值
                        actualResult = actualResult[index]
                        logger.info('将预期值按照填写的类型进行转换')
                        expectedValue = self.changeValue(expectedValue, expectedType)
                        compareResult = self.compareAssertValue(compareValue, actualResult, expectedValue)
                        logger.info('实际结果和预期结果比较的结果是{}'.format(compareResult))
                        if compareResult:
                            assertResult['msg'] = '用例执行成功'
                            if compareValue == '长度大于':
                                actualResult = len(actualResult)
                            msg = '对比期望，实际结果{}预期结果，字段【{}】对比成功,预期结果为:{},实际结果为:{}'.format(compareValue, param,
                                                                                        expectedValue,
                                                                                        actualResult)
                            logger.info(msg)
                            assertResultList.append(msg)
                            assertResult['assertResultList'] = assertResultList
                            continue
                        else:
                            assertResult['isPass'] = 'Fail'
                            assertResult['msg'] = '用例执行失败'
                            msg = '对比期望，实际结果{}预期结果，字段【{}】对比失败,预期结果为:{},实际结果为:{}'.format(compareValue, param,
                                                                                        expectedValue,
                                                                                        actualResult)
                            logger.info(msg)
                            assertResultList.append(msg)
                            assertResult['assertResultList'] = assertResultList
            except Exception as e:
                assertResult = {'code': code, 'isPass': 'Error', 'api': api_url, 'assertResultList': [],
                                'msg': '断言异常，请检查断言参数{}'.format(e)}
        return assertResult

    def searchSql(self, db_id, sql):
        """
        根据数据库查找对应的数据
        :param db_id:
        :param sql:
        :return:
        """
        if db_id == '' or sql == '':
            return False
        else:
            try:
                db_id = int(db_id)
                db_name = Database.objects.get(db_id=db_id).db_name
                db_host = Database.objects.get(db_id=db_id).db_host
                db_port = Database.objects.get(db_id=db_id).db_port
                db_user = Database.objects.get(db_id=db_id).db_user
                db_passwd = Database.objects.get(db_id=db_id).db_passwd
                sqlResult = self.executeSql(sql, db_name=db_name, host=db_host, user=db_user, passwd=db_passwd,
                                            port=db_port)
                return sqlResult
            except Exception as e:
                raise ConnectSqlError(e)

    def handleDataDriven(self, step, project_id=None, case_id=None):
        """
        1、判断是否需要数据驱动，如果需要则，nums至少要填写1
        2、获取需要需要被替换的字段列表，制造对应数量的数据驱动数量，保存在一个字典之中
        3、有几组则运行几次
        :param step:
        :return:
        """
        dataDrivenForm = step.get('dataDrivenForm') if 'dataDrivenForm' in step.keys() else None
        logger.info('数据驱动情况:{}'.format(dataDrivenForm))
        if dataDrivenForm and dataDrivenForm['checked']:
            nums = int(dataDrivenForm['nums'])
            queryTypeList = dataDrivenForm['queryList']
            queryTypeDict = {}
            paramService = ParamService(nums)
            for query in queryTypeList:
                queryName = query['queryName']
                queryType = query['queryType']
                queryId = query['queryId']
                paramType = Params.objects.get(param_id=int(queryId)).param_type
                paramList = Params.objects.get(param_id=int(queryId)).param_list
                result = paramService.runParam(paramType, queryType, data=paramList)
                queryTypeDict[queryName] = result
            for num in range(nums):
                queryDict = {}
                for queryKey in queryTypeDict.keys():
                    queryDict[queryKey] = queryTypeDict[queryKey][num]
                result = self.step(step, project_id=project_id, case_id=case_id, queryDict=queryDict)
                self.case_run.append(result)
        else:
            result = self.step(step, project_id=project_id, case_id=case_id)
            self.case_run.append(result)

    def step(self, step, project_id=None, case_id=None, queryDict=None):
        """
        获取到步骤中得信息
        :param step: 步骤
        :param project_id:用例中是否包含了项目id
        :param case_id:
        :return:
        """
        try:
            # logger.info('用例步骤请求详情信息{}'.format(step))
            stepDescription = step.get('stepDescription')
            logger.info('执行的用例步骤:{}'.format(stepDescription))
            if 'project_id' in step.keys():
                project_id = step.get('project_id')
            else:
                project_id = project_id
            projectEnvUrl = self.getEnvUrl(project_id)
            prj_url = projectEnvUrl.get('httpUrl')
            logger.info('执行的环境地址:{}'.format(prj_url))
            envType = projectEnvUrl.get('envType')
            logger.info('执行的项目环境所属:{}'.format(envType))
            api_id = step.get('api_id')
            logger.info('执行的接口id:{}'.format(api_id))
            api_name = step.get('api_name')
            logger.info('执行的接口名称:{}'.format(api_name))
            api_url = step.get('api_url')
            logger.info('执行的接口:{}'.format(api_url))
            method = step.get('method')
            logger.info('请求方式:{}'.format(method))
            data_type = step.get('data_type')
            logger.info('数据传输方式:{}'.format(data_type))
            url = prj_url + api_url
            logger.info('请求的地址:{}'.format(url))
            takeUpTimes = float(step.get('takeUpTime')) if 'takeUpTime' in step.keys() and step.get(
                'takeUpTime') != '' else 3
            logger.info('耗时校验：{}'.format(takeUpTimes))
            is_sign = step.get('is_sign')
            logger.info('是否需要签名:{}'.format('不需要' if is_sign == 0 else '需要'))
            request_case_id_list = step.get('requsetCaseList')
            logger.info('请求的前置用例:{}'.format(request_case_id_list))
            if request_case_id_list is not None and len(request_case_id_list) != 0:
                logger.info('判断有没有case列表，没有就进来')
                self.analyzeRequestCaseIdListData(request_case_id_list)
            requestJson = step.get('requestJson')
            if requestJson != '':
                logger.info('检测到json请求不为空:{}'.format(requestJson))
                requestJson = self.analyzeRequestRequestJson(requestJson)
            requestBodyList = step.get('requestBodyList')
            logger.info('获取到的requestBodyList:{}'.format(requestBodyList))
            request_body_list = self.analyzeRequestListData(requestBodyList, queryDict)
            requestHeaderList = step.get('requestHeaderList')
            logger.info('获取到的requestHeaderList:{}'.format(requestHeaderList))
            requestHeaderData = self.analyzeRequestListData(requestHeaderList, queryDict)
            requestBodyData = requestJson if requestJson else request_body_list
            logger.info('请求的body数据:{}'.format(requestBodyData))
            # 新康众签名逻辑
            if is_sign:
                logger.info('这个接口需要签名，走签名逻辑')
                signForm = self.getSessionIdAndSecret(envType)
                sessionId = signForm['sessionId']
                secret = signForm['secret']
                requestHeaderData['session-id'] = requestHeaderData['session-id'] if requestHeaderData[
                    'session-id'] else sessionId
                del requestBodyData['sign']
                sign = signByMd5(requestHeaderData, requestBodyData, secret)
                requestBodyData['sign'] = sign
            logger.info('请求的header数据:{}'.format(requestHeaderData))
            logger.info('请求后端')
            requestApiResult = self.requestApi(method=method, url=url,
                                               headers=requestHeaderData,
                                               data=requestBodyData,
                                               data_type=data_type, takeUpTime=takeUpTimes)
            # 加重试机制
            if self.get_target_value('code', requestApiResult, [])[1] == -9580106:
                logger.info('请求为无效的签名，再重新请求一次')
                secret = self.get_target_value('secret', requestApiResult, [])[0]
                session_id = self.get_target_value('session-id', requestApiResult, [])[0]
                requestHeaderData['session-id'] = session_id
                logger.info('打印secret：{}'.format(secret))
                del requestBodyData['sign']
                sign = signByMd5(requestHeaderData, requestBodyData, secret)
                requestBodyData['sign'] = sign
                logger.info('重新请求的header数据:{}'.format(requestHeaderData))
                logger.info('重新请求的body数据:{}'.format(requestBodyData))
                logger.info('再次请求后端')
                requestApiResult = self.requestApi(method=method, url=url,
                                                   headers=requestHeaderData,
                                                   data=requestBodyData,
                                                   data_type=data_type, takeUpTime=takeUpTimes)
            logger.info('请求接口返回的数据:{}'.format(requestApiResult))
            result = requestApiResult
            code = requestApiResult.get('code')
            logger.info('请求接口返回的code码:{}'.format(code))
            if code == 6:
                result = requestApiResult.get('result')
                acTakeUpTime = requestApiResult.get('acTakeUpTime')
                request_assert_list = step.get('responseAssertList')
                logger.info('请求接口正常，获取断言列表:{},进行数据剥离断言'.format(request_assert_list))

                result = self.analyzeRequestAssertListData(request_assert_list, requestHeaderData, requestBodyData,
                                                           result, code, api_url, acTakeUpTime)
                # 断言通过，将结果暂存在ApiResult表中，前置case跑得数据存在CaseResult
                self.saveResult(api_id, case_id, requestApiResult)
            else:
                result['api'] = api_url
                result['requestHeaderData'] = requestHeaderData
                result['requestBodyData'] = requestBodyData
            return result
        except Exception as e:
            api_url = step.get('api_url')
            logger.error('请求接口异常，错误信息{}'.format(e))
            return {'code': 7, 'isPass': 'Error', 'api': api_url, 'msg': '请求异常，"{}"'.format(e)}

    def dubboStep(self, step, case_id=None):
        """
        处理dubbo调用
        :param step:用例中的一个步骤
        :param api_id:接口id
        :param case_id:用例id
        :return:
        """
        try:
            api_id = step.get('api_id')
            project_id = step.get('project_id')
            envUrl = self.getEnvUrl(project_id)
            zkUrl = envUrl.get('zkUrl')
            zk_database = zkUrl if zkUrl != '' else step.get('zk_database')
            zk_api_name = step.get('zk_api_name')
            zk_api_method = step.get('api_url')
            requestDubboList = step.get('requestJsonList')
            requestDubboListStr = self.handleDubboRequestList(requestDubboList)
            requestDubboListStr = self.analyzeRequestRequestJson(requestDubboListStr)
            logger.info('开始连接zk:{}'.format(zk_database))
            getDubboService = GetDubboService(zk_database)
            dubboService = getDubboService.getDubboInfo(zk_api_name)
            host = dubboService.get('server_host')
            port = dubboService.get('server_port')
            dubbo = Dubbo(host, port)
            logger.info('开始dubbo请求')
            result = dubbo.invokeCommand(zk_api_name, zk_api_method, requestDubboListStr)
            code = result.get('code')
            if code == 6:
                result = result.get('result')
                request_assert_list = step.get('responseAssertList')
                logger.info('请求接口正常，获取断言列表:{},进行数据剥离断言'.format(request_assert_list))

                result = self.analyzeRequestAssertListData(request_assert_list, None, requestDubboListStr, result, code, zk_api_method)
                # 将结果暂存在ApiResult表中，前置case跑得数据存在CaseResult
                self.saveResult(api_id, case_id, result)
            else:
                result['api'] = zk_api_method
            return result
        except Exception as e:
            api_url = step.get('api_url')
            logger.error('请求接口异常，错误信息{}'.format(e))
            return {'code': 7, 'isPass': 'Error', 'api': api_url, 'msg': '请求异常，"{}"'.format(e)}

    def saveResult(self, api_id, case_id, requestApiResult):
        """
        保存执行结果，case_id存在就保存在case结果表中，不存在就保存在api结果表中
        :param api_id:
        :param case_id:
        :param requestApiResult:
        :return:
        """
        isExistIfId = ApiResult.objects.filter(api_id=api_id)
        if isExistIfId:
            logger.info('判断到api_id已经存在表中，将结果进行更新')
            isExistIfId.update(api_id=api_id, content=requestApiResult, update_time=datetime.datetime.now())
        else:
            logger.info('判断到api_id不存在表中，将结果进保存')
            if_result = ApiResult(api_id=api_id, content=requestApiResult)
            if_result.save()
        if case_id:
            logger.info('判断到case_id存在，将结果返回的数据存储在caseResult表中')
            isExistCaseId = CaseResult.objects.filter(case_id=case_id)
            if isExistCaseId:
                logger.info('判断到case_id已经存在，将结果进行更新')
                isExistCaseId.update(case_id=case_id, content=requestApiResult, update_time=datetime.datetime.now())
            else:
                logger.info('判断到case_id不存在，将结果进行保存')
                case_result = CaseResult(case_id=case_id, content=requestApiResult)
                case_result.save()

    def run_case(self):
        """
        控制用例运行，返回一个用例总的执行结果
        :return:
        """
        resultTotal = {'code': 6, 'isPass': 'Pass', 'msg': '用例执行成功', 'acTakeUpTime': '', 'assertResultList': [],
                       'results': []}
        assertResultLists = []
        for step in self.step_list:
            if step.get('request_method') == 'dubbo':
                step_info = self.dubboStep(step, case_id=self.case_id)
                self.case_run.append(step_info)
            else:
                self.handleDataDriven(step=step, case_id=self.case_id)
        for stepResult in self.case_run:
            code = stepResult.get('code')
            isPass = stepResult.get('isPass')
            api = stepResult.get('api')
            if 'assertResultList' in stepResult.keys():
                assertResultList = stepResult.get('assertResultList')
            else:
                msg = '接口:' + '【' + api + '】' + '返回的结果中存在错误，未走到断言'
                assertResultList = [msg]
            if code != 6 or isPass == 'Error' or isPass == 'Fail':
                resultTotal['code'] = code
                resultTotal['isPass'] = isPass
                msg = stepResult.get('msg')
                resultTotal['msg'] = msg
                assertResultLists = assertResultLists + assertResultList
            else:
                msg = '接口:' + '【' + api + '】' + '所有断言字段均正确'
                assertResultLists.append(msg)
                continue
        resultTotal['assertResultList'] = assertResultLists
        resultTotal['results'] = self.case_run
        return resultTotal
