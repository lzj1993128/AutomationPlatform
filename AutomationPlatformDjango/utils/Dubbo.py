import logging
import re
from urllib import parse
import json

# import dubbo_telnet
from kazoo.client import KazooClient

from common.base.BaseService import BaseService
from common.http.DubboError import DubboError

logger = logging.getLogger('log')


class Dubbo(BaseService):
    """
    通过telnet连接dubbo服务, 执行shell命令, 可用来调用dubbo接口
    """

    def __init__(self, host, port):
        self.connectDubbo = dubbo_telnet.connect(host, port)
        self.dubboError = DubboError()

    def checkResult(self, result):
        """
        处理服务端返回的结果
        :param result: 服务端返回的结果
        :return:
        """
        if result:
            code = self.get_target_value('code', result, [])[0]
            if code != 0:
                result = self.dubboError.error_status('error_code_01', result)
            else:
                result = self.dubboError.error_status('http_pass', result)
            return result
        else:
            result = self.dubboError.error_status('error_code_02', result)
            return result

    def invokeCommand(self, serviceName, serviceMethod, params):
        """
        执行invoke命令
        :param serviceName: 服务接口名
        :param serviceMethod: 服务方法名
        :param params: 具体参数
        :return:
        """
        if not isinstance(params, str) and isinstance(params, dict):
            logger.info('检测到不是str，转化一下')
            params = json.dumps(params)
        elif isinstance(params, int) or isinstance(params, str):
            params = '"{}"'.format(str(params))
        try:
            logger.info('打印服务接口名：{}，打印服务方法名：{}，打印请求的dubbo参数{}'.format(serviceName, serviceMethod, params))
            result = self.connectDubbo.invoke(serviceName, serviceMethod, params)
            logger.info('打印返回结果：', result)
            result = self.checkResult(result)
            return result
        except Exception as e:
            logger.error("执行命令异常,返回：{}".format(e))
            result = self.dubboError.error_status('error_code_03', '{}'.format(e))
            return result


class GetDubboService:
    """
    获取zk注册链接地址
    """

    def __init__(self, host):
        self.zk = KazooClient(hosts=host)
        self.zk.start()  # 与zookeeper连接

    def getDubboInfo(self, dubbo_service):
        node = self.zk.get_children('/dubbo/' + dubbo_service + '/providers')
        logger.info('打印节点：{}'.format(node))
        if node:
            server = parse.unquote(node[0])
            # 匹配服务端
            dubbore = re.compile(r"^dubbo://([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+)", re.I)
            result = dubbore.match(server)
            if result:
                result = result.group(1)
                logger.info("获取到dubbo部署信息" + result)
                return {"server_host": result.split(":")[0], "server_port": result.split(":")[1]}
        self.zk.stop()


if __name__ == '__main__':
    host = 'zk1.cluster.carzone360.net:2181'
    zk1 = GetDubboService(host)
    result = zk1.getDubboInfo('com.ncarzone.data.di.visual.brain.facade.visual.VisualCategoryFacade')
    server_host = result.get("server_host")
    server_port = result.get("server_port")
    param = {
        "class": "com.ncarzone.data.di.visual.brain.facade.model.base.BaseRequest",
        "regionId": "0008",
        "regionType": 1,
        "requestDate": "2020-08",
    }

    param = json.dumps(param)
    print(param)
    server_name = "com.ncarzone.data.di.visual.brain.facade.visual.VisualCategoryFacade"
    dubbo_method = "queryCategoryLabels"

    conn = dubbo_telnet.connect(server_host, server_port)
    result = conn.invoke(server_name, dubbo_method, param)
    print(result)
