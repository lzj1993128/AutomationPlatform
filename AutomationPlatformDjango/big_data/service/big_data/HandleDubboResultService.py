from common.base.BaseService import BaseService


class HandleDubboResultService(BaseService):
    def __init__(self, dubbo_result, reponse_field):
        self.dubbo_result = dubbo_result
        self.reponse_firld = reponse_field

    def handleDubboResult(self):
        """
        将返回的dubbo接口结果进行处理
        :return:
        """
        result = self.get_target_value(self.reponse_firld, self.dubbo_result, [])[0]
        return result
