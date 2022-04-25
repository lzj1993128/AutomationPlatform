from api.exception.plan.PlanServiceException import LackMustRequestParam
from common.base.BaseService import BaseService


class SaveInterfaceService(BaseService):
    def checkSaveRequestParam(self, requestData):
        """
        确认请求参数是否缺失
        :param requestData:
        :return:
        """
        if 'project_id' not in requestData.keys() or requestData.get('project_id') == '':
            msg = '请将项目名称填写完整'
            raise LackMustRequestParam(msg)
        if 'module_id' not in requestData.keys() or requestData.get('module_id') == '':
            msg = '请将模块名称填写完整'
            raise LackMustRequestParam(msg)
