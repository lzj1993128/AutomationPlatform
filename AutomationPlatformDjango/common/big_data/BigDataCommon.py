from common.base.BaseService import BaseService
from utils.Dubbo import Dubbo, GetDubboService


class BigDataCommon(BaseService):

    def handleRequestDubboHeaders(self):
        """
        主要加上ac-seesion-id，有两个dubbo接口，先获取cs，在把cs当参数传递给获取ac-session-id的dubbo接口
        :param headers: dict，header
        :return:
        """
        zkHost = 'zk1.cluster.carzone360.net'
        dubboMethodName = 'com.ncarzone.authcenter.facade.service.login.LoginFacade'
        # 获取cs
        dubboApiName1 = 'createUserSession'
        # 获取ac-seesion-id
        dubboApiName2 = 'getSessionId'
        # 员工工号
        requestDubboListStr = '"333743"'

        getDubboService = GetDubboService(zkHost)
        dubboService = getDubboService.getDubboInfo(dubboMethodName)
        host = dubboService.get('server_host')
        port = dubboService.get('server_port')
        dubbo = Dubbo(host, port)
        result = dubbo.invokeCommand(dubboMethodName, dubboApiName1, requestDubboListStr)
        cs = '"{}"'.format(self.get_target_value('data', result, [])[0])
        acResult = dubbo.invokeCommand(dubboMethodName, dubboApiName2, cs)
        while 'data' not in acResult['result'].keys():
            acResult = dubbo.invokeCommand(dubboMethodName, dubboApiName2, cs)
        acSessionId = self.get_target_value('data', acResult, [])[0]
        return acSessionId


if __name__ == '__main__':
    d = BigDataCommon()
    s = d.handleRequestDubboHeaders()
    print(s)