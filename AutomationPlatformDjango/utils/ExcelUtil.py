import xlrd
import xlwt
from xlutils.copy import copy


class ExcelUtil:
    def __init__(self, file=None, flag=False, num_sheet=0):
        """
        :param file:excel文件名
        :param flag:用来判断是否需要创建表格
        """
        self.file_name = file
        if flag:
            self.creatExcel()
        self.data = self.getSheetData(num_sheet)

    def creatExcel(self):
        work_book = xlwt.Workbook(encoding='utf-8')
        work_book.add_sheet('Sheet1')
        work_book.save(self.file_name)

    def write_excel(self, row, value, cell=0, num_sheet=0):
        book1 = xlrd.open_workbook(self.file_name)
        # 需要先拷贝一份原来的excel
        book2 = copy(book1)
        # 获取第几个sheet页，book2现在的是xlutils里的方法，不是xlrd的
        sheet = book2.get_sheet(num_sheet)
        sheet.write(row, cell, value)
        book2.save(self.file_name)

    def getSheetData(self, num_sheet):
        """
        获取sheet内容
        :param num_sheet:sheet下标
        :return:
        """
        data = xlrd.open_workbook(self.file_name)
        tables = data.sheets()[num_sheet]
        return tables

    def getRows(self):
        """
        获取sheet总的行数
        :return:
        """
        tables = self.data
        return tables.nrows

    def getCols(self):
        """
        获取一个多少列
        :return:
        """
        tables = self.data
        return tables.ncols

    def getCellValue(self, row, col, num_sheet=0):
        """
        获取单元格内容
        :param row: 行
        :param col: 列
        :param num_sheet:第几个sheet表
        :return:
        """
        table = self.getSheetData(num_sheet)
        data = table.cell(row, col)
        if data.ctype == 2 and data.value % 1 == 0:
            data = int(data.value)
        elif data.ctype == 1:
            data = data.value
        else:
            pass
        return data

    def getRowValues(self, row):
        """
        获取某一行内容
        :param row: 行
        :return:
        """
        row_data = self.data.row_values(row)
        return row_data

    def getColsValues(self, col_id):
        """
        获取某一列数据
        :param col_id:列
        :return:
        """
        cols_data = self.data.col_values(col_id)
        return cols_data
