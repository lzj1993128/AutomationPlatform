import random
import time
import datetime

import logging
logger = logging.getLogger('log')

class ParamService:
    def __init__(self, nums):
        """
        初始化数据
        :param nums: 需要传入的组数
        :param data: 需要处理的字典
        """
        self.nums = nums

    def sequenceDict(self, data, queryType):
        """
        顺序字典逻辑
        :return:
        """
        data = data.split(',')
        sequenceList = [data[i] if i < len(data) else data[int(i % len(data))] for i in range(self.nums)]
        sequenceList = [self.changeValue(j, queryType) for j in sequenceList]
        return sequenceList

    def randomDict(self, data, queryType):
        """
        随机字典
        :return:
        """
        data = data.split(',')
        randomList = [random.choice(data) for i in range(self.nums)]
        randomList = [self.changeValue(j, queryType) for j in randomList]
        return randomList

    def getNewYear(self):
        """
        获取最新年份
        :return:
        """
        year = time.strftime("%Y", time.localtime())
        yearList = [year for i in range(self.nums)]
        return yearList

    def getNewDateSubOne(self):
        """
        昨日
        :return:
        """
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime('%Y-%m-%d')
        yesterdayList = [yesterday for i in range(self.nums)]
        return yesterdayList

    def getNewMonth(self):
        """
        获取最新日期
        :return:
        """
        month = time.strftime("%Y-%m", time.localtime())
        monthList = [month for i in range(self.nums)]
        return monthList

    def getNewDate(self):
        """
        获取最新日期
        :return:
        """
        date = time.strftime("%Y-%m-%d", time.localtime())
        dateList = [date for i in range(self.nums)]
        return dateList

    def changeValue(self, value, typeValue):
        """
        将前端body值根据类型进行转化，请求服务端接口
        :param value:值
        :param typeValue:需要转换的类型
        :return:
        """
        logger.info('将{}进行类型转换'.format(value))
        if typeValue == 'str':
            logger.info('检测到值是str类型，转换成str类型')
            value = str(value)
        elif typeValue == 'int':
            logger.info('检测到值是整数类型，转换成int类型')
            value = int(value)
        elif typeValue == 'float':
            logger.info('检测到值是浮点类型，转换成float类型')
            value = float(value)
        elif typeValue == 'boolean':
            logger.info('检测到值是布尔类型，转换成布尔类型')
            value = True if value == 'true' or value == 'True' else False
        else:
            value = value
        return value

    def runParam(self, paramType, queryType, data=None):
        """
        :param queryType:需要把queryType处理成什么类型
        :param paramType: 数据驱动类型
        :param data: 需要处理的字典：如['2021-01','2021-02']
        :return: 
        """
        if paramType == 0:
            result = self.sequenceDict(data, queryType)
        if paramType == 1:
            result = self.randomDict(data, queryType)
        if paramType == 3:
            result = self.getNewYear()
        if paramType == 2:
            result = self.getNewMonth()
        if paramType == 4:
            result = self.getNewDate()
        if paramType == 5:
            result = self.getNewDateSubOne()
        return result
