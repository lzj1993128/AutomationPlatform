from common.base.BaseService import BaseService
from api.models import Project, Module
from django.db.models import Q
from utils.PageUtil import PageUtil

import logging

logger = logging.getLogger('log')


class CaseTreeService(BaseService):
    def __init__(self):
        self.pageUtil = PageUtil()
        pass

    def getCaseTree(self):
        """
        获取项目树包含的项目以及模块
        :return: caseTreeList,用例树列表
        """
        caseTreeList = []
        caseTreeDict = {}
        projectChildrenList = []
        projectQuery = Project.objects.filter(is_delete=0)
        projectList = self.pageUtil.searchSqlFieldData(projectQuery)
        for project in projectList:
            projectChildrenDict = {}
            prj_id = project.get('prj_id')
            projectChildrenDict['prj_id'] = prj_id
            projectChildrenDict['module_id'] = ''
            projectChildrenDict['label'] = project.get('prj_name')
            moduleChildrenList = []
            moduleQuery = Module.objects.filter(Q(project_id=prj_id) & Q(is_delete=0))
            moduleList = self.pageUtil.searchSqlFieldData(moduleQuery)
            for module in moduleList:
                moduleChildrenDict = dict()
                moduleChildrenDict['prj_id'] = prj_id
                moduleChildrenDict['module_id'] = module.get('module_id')
                moduleChildrenDict['label'] = module.get('module_name')
                moduleChildrenList.append(moduleChildrenDict)
            projectChildrenDict['children'] = moduleChildrenList
            projectChildrenList.append(projectChildrenDict)
        caseTreeDict['children'] = projectChildrenList
        caseTreeDict['label'] = '全部项目'
        caseTreeList.append(caseTreeDict)
        return caseTreeList
