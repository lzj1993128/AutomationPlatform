# -*- coding: utf-8 -*-


class BaseResponse:
    def __init__(self):
        self.SUCCESS_CODE = 1
        self.ERROR_CODE = 0
        self.success = True
        self.message = ""
        self.data = dict()

