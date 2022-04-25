class DubboError:
    def error_status(self, error_name, info):
        """
        错误过滤
        :param error_name:
        :param info:返回结果信息
        :return:
        """
        error_status = {
            'error_code_01': {'code': 1, 'isPass': 'Error', 'msg': '返回结果结果code非0', 'result': info},
            'error_code_02': {'code': 2, 'isPass': 'Error', 'msg': '返回结果为空', 'result': info},
            'error_code_03': {'code': 3, 'isPass': 'Error', 'msg': '执行dubbo异常', 'result': info},
            'http_pass': {'code': 6, 'result': info}  # 返回数据没有错误
        }
        return error_status.get(error_name)