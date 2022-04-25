import paramiko
import logging

logger = logging.getLogger('log')


class MSLogUtil:
    def connectMS(self, ip, port, user, password, log_path):
        """
        连接服务器获取错误日志,默认2000行
        :param ip: 服务器ip
        :param port: 服务器端口，默认22
        :param user: 用户名
        :param password: 密码
        :param log_path: 微服务日志所在路径
        :return:
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 建立连接
            ssh.connect(ip, port, user, password, timeout=10)
            # 获取日志倒数行数2000行
            command = 'tail -n 2000 {}'.format(log_path)
            stdin, stdout, stderr = ssh.exec_command(command)
            # 输出命令执行结果
            result = stdout.read()
            # 关闭连接
            ssh.close()
            return result
        except Exception as e:
            logger.log('连接服务器异常{}'.format(e))
