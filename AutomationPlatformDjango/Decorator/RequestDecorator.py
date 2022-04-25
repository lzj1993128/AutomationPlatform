from django.http import JsonResponse
from common.reponse.SuccessResponse import SuccessResponse
from common.reponse.ErrorResponse import ErrorResponse
from api.models import User

success = SuccessResponse()
error = ErrorResponse()
import logging

logger = logging.getLogger('log')


def requestIntercept(func):
    def interceptToken(request):
        logger.info('检查request中是否包含token和userId')
        logger.info('执行的请求为{}():'.format(func.__name__))
        token = request.META.get('HTTP_TOKEN')
        userId = request.META.get('HTTP_USERID')
        try:
            logger.info('获取数据库中存在的token')
            modelToken = User.objects.get(user_id=userId).token
        except Exception as e:
            logger.info('获取数据库中的token异常，说明userid为空或者不存在')
            modelToken = None
        if token == None and userId == None:
            responseData = error.error_response(msg='请先登录')
            return JsonResponse(data=responseData, safe=False)
        # elif modelToken != None and modelToken != token:
        #     # 50008， token过期
        #     code = 50008
        #     responseData = error.error_response(msg='登录信息已过期', code=code)
        #     return JsonResponse(data=responseData, safe=False)
        else:
            logger.info('两个token一致')
            result = func(request)
            return result

    return interceptToken
