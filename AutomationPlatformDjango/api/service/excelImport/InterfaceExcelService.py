from api.models import Interface, User
from utils.ExcelUtil import ExcelUtil
from django.db.models import Q
import logging

logger = logging.getLogger('log')


class ExcelService:
    def __init__(self, excel, userId):
        self.excelUtil = ExcelUtil(excel)
        self.userId = userId
        pass

    def addRowData(self):
        """
        获取每一个行的数据，将数据写入数据库，跳过已经存在的接口
        :return:
        """
        # 获取总行数
        rows = self.excelUtil.getRows()
        if rows > 1:
            logger.info('开始导入接口')
            runRow = rows - 2
            for row in range(runRow):
                row = row + 2
                api_name = self.excelUtil.getCellValue(row, 0)
                api_url = self.excelUtil.getCellValue(row, 1)
                method = self.excelUtil.getCellValue(row, 2)
                data_type = self.excelUtil.getCellValue(row, 3)
                project = int(self.excelUtil.getCellValue(row, 4))
                module = int(self.excelUtil.getCellValue(row, 5))
                request_header_param = self.excelUtil.getCellValue(row, 6) if self.excelUtil.getCellValue(row, 6) else None
                request_body_param = self.excelUtil.getCellValue(row, 7) if self.excelUtil.getCellValue(row, 7) else None
                is_sign = self.excelUtil.getCellValue(row, 8)
                description = self.excelUtil.getCellValue(row, 9)
                developer = self.excelUtil.getCellValue(row, 10)
                interface = Interface.objects.filter(Q(is_delete='0') & Q(api_url=api_url) & Q(method=method))
                username = User.objects.get(user_id=self.userId).username
                if interface.count() > 0:
                    logger.info("已经存在这个接口，跳过")
                    continue
                else:
                    logger.info("数据库中不存在这个接口，可以导入")
                    api = Interface(api_name=api_name, api_url=api_url, method=method, data_type=data_type,
                                    creator=username,request_method='http', requestJsonList=[],
                                    project_id=project, module_id=module, request_header_param=request_header_param,
                                    request_body_param=request_body_param, is_sign=is_sign, description=description, developer=developer)
                    api.save()
            logger.info('导入接口结束')
        else:
            logger.info('无需处理数据')
