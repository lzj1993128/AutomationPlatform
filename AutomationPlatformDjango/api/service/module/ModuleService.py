# -*- coding: utf-8 -*-
from api.models import Module
from utils.PageUtil import PageUtil
from django.db.models import Q


class ModuleService:
    def __init__(self, prj_id, moduleData):
        self.prj_id = prj_id
        self.moduleData = moduleData
        self.msg = ''
        self.page = PageUtil()

    def saveModule(self):
        """
        批量保存名字
        :param prj_id:
        :param moduleData:
        :return:
        """
        if isinstance(self.moduleData, str):
            old_module_name = Module.objects.filter(Q(project_id=self.prj_id) & Q(is_delete='0'))
            fields = ['module_name']
            old_module_list = []
            old_module_name_list = self.page.searchSqlFieldData(old_module_name, fields)
            for i in old_module_name_list:
                old_module_list.append(i['module_name'])
            if self.moduleData in old_module_list:
                self.msg = '已经存在了这个模块'
            else:
                Module(module_name=self.moduleData, project_id=self.prj_id).save()
                self.msg = '保存成功'
        else:
            self.msg = '传进来的模块为空或者类型错误'
        return self.msg
