import json
from datetime import datetime

from api.exception.plan.PlanServiceException import LackMustRequestParam
from api.models import CaseLog, Case, User
from common.base.BaseService import BaseService


class SaveCaseService(BaseService):
    def checkSaveRequestParam(self, requestData):
        """
        确认请求参数是否正确
        :param requestData:
        :return:
        """
        caseForm = requestData.get('case_info')
        if 'case_name' not in caseForm.keys() or caseForm.get('case_name') == '':
            msg = '请将用例名称填写完整'
            raise LackMustRequestParam(msg)
        if 'bd_id' not in caseForm.keys() or caseForm.get('bd_id') == '':
            msg = '请选择业务域'
            raise LackMustRequestParam(msg)
        if 'project_id' not in requestData.keys() or requestData.get('project_id') == '':
            msg = '请将项目名称填写完整'
            raise LackMustRequestParam(msg)
        if 'module_id' not in requestData.keys() or requestData.get('module_id') == '':
            msg = '请将模块名称填写完整'
            raise LackMustRequestParam(msg)
        if 'step_info' not in requestData.keys() or len(requestData.get('step_info')) == 0:
            msg = '至少添加一个步骤再保存'
            raise LackMustRequestParam(msg)

    def saveCase(self, requestData, userId):
        """
        保存用例
        :param requestData: 请求参数保存
        :return:
        """
        try:
            case_id = requestData.get('case_id')
            opt_type = requestData.get('opt_type')
            case_info = requestData.get('case_info')
            case_name = case_info.get('case_name')
            description = case_info.get('description')
            bd_id = case_info.get('bd_id')
            api_list = case_info.get('api_list')
            project_id = requestData.get('project_id')
            module_id = requestData.get('module_id')
            case_type = int(requestData.get('case_type'))
            online_type = int(requestData.get('online_type'))
            step_info = str(json.dumps(requestData.get('step_info'))) if requestData.get('step_info') else None
            if case_type == 0:
                caseNums = self.countCaseNums(step_info) if step_info else 0
            else:
                caseNums = 1 if step_info and len(step_info) != 0 else 0
            username = User.objects.get(user_id=userId).username
            if opt_type == '':
                case = Case(case_name=case_name, description=description,
                            case_type=case_type, online_type=online_type,
                            step_info=step_info, project_id=project_id, bd_id=bd_id, api_list=api_list,
                            module_id=module_id, creator=username, update_person=username, case_nums=caseNums)
                case.save()
            elif opt_type == 'edit':
                Case.objects.filter(case_id=case_id).update(case_name=case_name, description=description,
                                                            api_list=api_list,
                                                            case_type=case_type, online_type=online_type,
                                                            step_info=step_info, project_id=project_id, bd_id=bd_id,
                                                            module_id=module_id, update_person=username,
                                                            update_time=datetime.now(), case_nums=caseNums)
                case_log = CaseLog(case_id=case_id, case_name=case_name, description=description, api_list=api_list,
                                   case_type=case_type, online_type=online_type,
                                   step_info=step_info, project_id=project_id, bd_id=bd_id,
                                   module_id=module_id, creator=userId)
                case_log.save()
            else:
                case = Case.objects.get(pk=case_id)
                case.pk = None
                case = Case(case_name=case_name, description=description, api_list=api_list,
                            case_type=case_type, online_type=online_type,
                            step_info=step_info, project_id=project_id, bd_id=bd_id,
                            module_id=module_id, creator=username, update_person=username, case_nums=caseNums)
                case.save()
        except LackMustRequestParam:
            msg = '保存用例失败'
            raise LackMustRequestParam(msg)

    def countCaseNums(self, stepList):
        """
        统计用例总数
        :param stepList:
        :return:
        """
        nums = 0
        stepList = json.loads(stepList)
        for step in stepList:
            if 'dataDrivenForm' in step.keys():
                dataDrivenForm = step.get('dataDrivenForm')
                num = int(dataDrivenForm.get('nums'))
                num = num if num else 1
            else:
                num = 1
            nums = nums + num
        return nums