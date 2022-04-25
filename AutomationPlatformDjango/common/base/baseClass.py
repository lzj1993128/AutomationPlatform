# -*- coding: utf-8 -*-
import time
import hashlib
import json

import logging

logger = logging.getLogger('log')


def getBodyData(data):
    """
    通用方法，将前端穿过来得数据处理成字典
    :param data:
    :return:
    """
    try:
        if isinstance(data, bytes):
            data = json.loads(data.decode())
        else:
            data = eval(data)
        return data
    except Exception as e:
        logger.error('处理成字典异常{}'.format(e))
    finally:
        return data


def md5(username):
    """
    获取token
    :param username:
    :return:
    """
    now = str(time.time())
    md5_obj = hashlib.md5(bytes(username + 'mamahaotest', encoding='utf8'))
    md5_obj.update(bytes(now, encoding='utf8'))
    return md5_obj.hexdigest()


def get_target_value(key, dic, tmp_list):
    """
    循环遍历对应的字段,并将数据保存为列表
    :param key: 目标key值
    :param dic: JSON数据
    :param tmp_list: 用于存储获取的数据
    :return: list
    """
    if not isinstance(dic, dict) or not isinstance(tmp_list, list):
        logger.error('这个不是字典类型或者这个不是列表类型')
        return '这个不是字典类型或者这个不是列表类型'
    if key in dic.keys():
        tmp_list.append(dic[key])
    else:
        for value in dic.values():
            if isinstance(value, dict):
                get_target_value(key, value, tmp_list)
            elif isinstance(value, (list, tuple)):
                _get_value(key, value, tmp_list)
    return tmp_list


def _get_value(key, val, tmp_list):
    for val_ in val:
        if isinstance(val_, dict):
            get_target_value(key, val_, tmp_list)
        elif isinstance(val_, (list, tuple)):
            _get_value(key, val_, tmp_list)


def isDictVuleNone(data):
    """
    删除页码，判断这个参数是否为空
    :param data:字典类型
    :return:
    """
    lists = []
    for key in list(data.keys()):
        if key == 'page' or key == 'pageSize':
            del data[key]
        else:
            if data[key] == '':
                del data[key]
            else:
                lists.append(data[key])
    if lists:
        return True
    else:
        return False


def isNone(data):
    """
    判断数据是否为空
    :param data:
    :return:
    """
    if data is None:
        return ''
    else:
        return data