import hashlib
import json
import logging

logger = logging.getLogger('log')

def sign_2(strSign):
    """
    生成md5命令
    :param strSign:
    :return:
    """
    sign = hashlib.md5()
    sign.update(strSign.encode(encoding='utf-8'))
    sign = sign.hexdigest().upper()
    return sign


def signByMd5(headers, bodys, secret):
    """
    nz签名逻辑，输入header和bodys生成对应的签名
    :param headers:
    :param bodys:
    :return:
    """
    # 将header中参数添加到body中
    if 'data' in bodys.keys():
        data = bodys['data']
        data = json.dumps(data) if len(data.keys())>0 else '{}'
        bodys['data'] = data
    for header in headers.keys():
        bodys[header] = headers[header]
    # 将bodys中的key进行排序，然后生成一个新的字典
    sortedBodys = sorted(bodys)
    newDicts = dict.fromkeys(sortedBodys)
    #  将字典中的key重新赋上value
    for i in newDicts.keys():
        newDicts[i] = bodys.get(i)
    strSign = ''
    # 将body按照规则重新生成字符串 key1value1key2value2...这样的形式
    for i in newDicts.keys():
        t = str(i) + str(newDicts.get(i))
        strSign = strSign + t
    # 按照规则头部加上secret
    strSign = secret + strSign
    logger.info('打印排序后的值：{}'.format(strSign))
    # 把添加到body中的header参数重新删除
    for i in headers.keys():
        del bodys[i]
    sign = sign_2(strSign)
    logger.info('打印签名：{}'.format(sign))
    return sign
