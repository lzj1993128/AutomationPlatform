import json
import logging
import os
import re
import time
import zipfile

import pymysql

from api.models import Env
from utils.RequestUtil import RunMethod

logger = logging.getLogger('log')


class BaseService:
    def get_target_value(self, key, dic, tmp_list):
        """
        循环遍历对应的字段,并将数据保存为列表
        :param key: 目标key值
        :param dic: JSON数据
        :param tmp_list: 用于存储获取的数据
        :return: list
        """
        # if not isinstance(dic, dict) or not isinstance(tmp_list, list):
        #     return '这个不是字典类型'
        if isinstance(dic, list):
            for i in dic:
                if isinstance(i, dict):
                    if key in i.keys():
                        tmp_list.append(i[key])
                    else:
                        for value in i.values():
                            if isinstance(value, dict):
                                self.get_target_value(key, value, tmp_list)
                            elif isinstance(value, (list, tuple)):
                                self._get_value(key, value, tmp_list)
                else:
                    continue
        if isinstance(dic, dict):
            if key in dic.keys():
                tmp_list.append(dic[key])
            for value in dic.values():
                if isinstance(value, dict):
                    self.get_target_value(key, value, tmp_list)
                elif isinstance(value, (list, tuple)):
                    self._get_value(key, value, tmp_list)
        return tmp_list

    def _get_value(self, key, val, tmp_list):
        for val_ in val:
            if isinstance(val_, dict):
                self.get_target_value(key, val_, tmp_list)
            elif isinstance(val_, (list, tuple)):
                self._get_value(key, val_, tmp_list)

    def changeType(self, val1, val2):
        """
        强制转换,val2转换成val1的类型
        :param val1:比较值1
        :param val2: 比较值2
        :return:
        """
        if isinstance(val1, str):
            val2 = str(val2)
        elif isinstance(val1, bool):
            val2 = True if val2 == 'true' else False
        elif isinstance(val1, int):
            val2 = int(val2)
        return val2

    def requestApi(self, method, url, headers=None, data=None, data_type='data', takeUpTime=None):
        """
        获取方法请求的方法
        :param method:请求类型
        :param url:请求地址
        :param data:请求参数
        :param header:请求头
        :return:
        """
        requestsApi = RunMethod()
        res = None
        if method == 'post':
            if data_type == 'json':
                res = requestsApi.post_main(url=url, headers=headers, json=data, takeUpTime=takeUpTime)
            if data_type == 'data':
                res = requestsApi.post_main(url=url, headers=headers, data=data, takeUpTime=takeUpTime)
        else:
            res = requestsApi.get_main(url=url, params=data, headers=headers, takeUpTime=takeUpTime)
        return json.loads(json.dumps(res, ensure_ascii=False))

    def _mysql_link(self, de_name, host=None, user=None, passwd=None, port=3306):
        '''
        数据库连接
        :param de_name:
        :return:
        '''
        try:
            db = pymysql.connect(host=host,
                                 port=port,
                                 user=user,
                                 passwd=passwd,
                                 db=de_name,
                                 charset='utf8')
            return db
        except Exception as e:
            logger.error('数据库连接异常{}'.format(e))

    def executeSql(self, sql, db_name='di_visual_brain', host='192.168.10.70', user='root', passwd='mamahao',
                   port=3306):
        db = self._mysql_link(db_name, host, user, passwd, port)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        result = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
        return result

    def get_now(self):
        """
        获取当前时间时间戳
        :return:
        """
        t = time.time()
        now_time = lambda: int(round(t * 1000))
        return now_time()

    def zipDir(self, dirpath, outPath):
        """
        压缩指定文件夹
        :param dirpath: 目标文件夹路径
        :param outPath: 压缩文件保存路径+xxxx.zip
        :return: 无
        """
        zip = zipfile.ZipFile(outPath, "w", zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(dirpath):
            # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
            fpath = path.replace(dirpath, '')
            for filename in filenames:
                if filename.split('.')[1] == 'zip':
                    continue
                else:
                    zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()

    def envUrl(self, project_id, envData):
        """
        返回各个接口所需要的环境地址，根据项目id判断
        :param project_id: 传进一个接口储存的项目id参数
        :return: 项目url
        """
        try:
            url = ''
            for env in envData:
                prj_id = env.get('selectEvnPrject')
                other_url = env.get('other_url')
                if project_id == prj_id:
                    if other_url == '':
                        env_id = int(env.get('selectEvnUrl'))
                        url = Env.objects.get(env_id=env_id).env_url
                    else:
                        url = other_url
            logger.info('请求的url地址为:{}'.format(url))
            return url
        except Exception as e:
            logger.error(e)

    def handleDubboRequestList(self, requestDubboRequestList):
        """
        处理dubbo测试传递过来的参数
        :param requestDubboRequestList:
        :return:
        """
        if isinstance(requestDubboRequestList, str):
            requestDubboRequestList = json.loads(requestDubboRequestList)
        requestJsonList = self.get_target_value('requestJson', requestDubboRequestList, [])
        requestJsonListStr = ','.join(requestJsonList)
        requestJsonListStr = re.sub('\s+', '', requestJsonListStr.strip())
        logger.info('处理过的请求参数:{}'.format(requestJsonListStr))
        return requestJsonListStr
