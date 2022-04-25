from api.models import User
from common.base.BaseService import BaseService


class UserService(BaseService):
    def checkUserName(self, username):
        """
        确认用户是否存在
        :param username:
        :return:
        """
        isExist = User.objects.filter(username=username)
        if isExist.count() == 0:
            return True
        else:
            return False

    def savaUser(self, username, role_id, password, nickname, phone):
        """
        保存用户
        :param username: 用户名称
        :param role_id: 权限id
        :param password: 密码
        :return:
        """
        isExist = self.checkUserName(username)
        if isExist:
            user = User(username=username, role_id=role_id, password=password, nickname=nickname, phone=phone)
            user.save()
            msg = '保存用户成功'
        else:
            msg = '用户名已存在'
        return msg
