class HttpError:
    def error_status(self, error_name, error_info, requestDiff):
        error_status = {
            'error_code_01': {'code': 1, 'isPass': 'Error', 'msg': 'http返回状态非200', 'acTakeUpTime': requestDiff, 'result': error_info},  #http返回状态非200
            'error_code_02': {'code': 2, 'isPass': 'Error', 'msg': '请求的接口结果无数据',  'acTakeUpTime': requestDiff, 'result': error_info},  # 返回的结果无数据
            'error_code_03': {'code': 3, 'isPass': 'Error', 'msg': '请求的接口返回的结果存在‘error’或者‘error_code’', 'acTakeUpTime': requestDiff, 'result': error_info},  # 返回的结果存在‘error’或者‘error_code’
            'error_code_04': {'code': 4, 'isPass': 'Error', 'msg': '请求的接口返回的结果存在false', 'acTakeUpTime': requestDiff, 'result': error_info},  # 返回的结果存在false
            'error_code_05': {'code': 5, 'isPass': 'Error', 'msg': '请求的接口返回的数据不能被序列化', 'acTakeUpTime': requestDiff, 'result': error_info},  # 返回的数据不能被序列化
            'http_pass': {'code': 6, 'acTakeUpTime': requestDiff},  # 返回数据没有错误
            'error_code_06': {'code': 8, 'isPass': 'Fail', 'msg': '请求接口消耗时间不通过', 'acTakeUpTime': requestDiff, 'result': error_info}
        }
        return error_status.get(error_name)