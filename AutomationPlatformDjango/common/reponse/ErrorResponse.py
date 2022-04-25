# -*- coding: utf-8 -*-
from common.reponse.BaseResponse import BaseResponse


class ErrorResponse(BaseResponse):

    def __init__(self):
        super(ErrorResponse, self).__init__()

    def error_response(self, msg='失败', code=200):
        self.data = dict()
        self.data['success'] = False
        self.data['message'] = msg
        self.data['code'] = code
        return self.data
