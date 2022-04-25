# -*- coding: utf-8 -*-
from common.reponse.BaseResponse import BaseResponse


class SuccessResponse(BaseResponse):
    def __init__(self):
        super(SuccessResponse, self).__init__()

    def success_response(self, msg='请求成功', code=200):
        self.data = dict()
        self.data['success'] = self.success
        self.data['message'] = msg
        self.data['code'] = code
        return self.data
