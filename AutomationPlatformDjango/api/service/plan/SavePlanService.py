from common.base.BaseService import BaseService
from api.exception.plan.PlanServiceException import LackMustRequestParam


class SavePlanService(BaseService):
    def checkSaveRequestParam(self, requestData):
        """
        确认请求参数是否正确
        :param requestData:
        :return:
        """
        planForm = requestData.get('planForm')
        if 'plan_name' not in planForm.keys() or planForm.get('plan_name') == '':
            msg = '请将计划名称填写完整'
            raise LackMustRequestParam(msg)
        if 'cron' not in planForm.keys() or planForm.get('cron') == '':
            msg = '请将执行时间填写完整'
            raise LackMustRequestParam(msg)
        if 'online_type' not in planForm.keys() or planForm.get('online_type') == '':
            msg = '请将执行环境填写完整'
            raise LackMustRequestParam(msg)
        if not requestData.get('projectList') and not requestData.get('caseList') and not requestData.get('bigDataList'):
            msg = '请选择用例'
            raise LackMustRequestParam(msg)
