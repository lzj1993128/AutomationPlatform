import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from api.models import Email
from utils.PageUtil import PageUtil

import logging

logger = logging.getLogger('log')
pageUtil = PageUtil()


class EmailUtil:
    # 定义发送邮件

    def sendEmail(self, report, to, file_new=None, mail_title='接口自动化平台自动化测试报告'):
        userQuery = Email.objects.filter(email_type='1')
        userList = pageUtil.searchSqlFieldData(userQuery)
        if len(userList) == 0:
            logger.info('发件人邮箱为空,无法发送邮件,请填写发件人邮箱')
        else:
            logger.info('发件人信息为{}'.format(userList))
            user = userList[0]
            email_name = user.get('email_name')
            email_address = user.get('email_address')
            email_password = user.get('email_password')
            smtp_address = user.get('smtp_address')
            smtp_port = int(user.get('smtp_port'))
            _to = to
            # 如名字所示Multipart就是分多个部分
            msg = MIMEMultipart()
            msg["Subject"] = mail_title
            msg["From"] = email_name
            msg["To"] = ','.join(_to)

            # ---这是文字部分---
            part1 = MIMEText(report, _subtype='html', _charset='utf-8')
            msg.attach(part1)

            # ---这是附件部分---
            # xlsx类型附件
            if isinstance(file_new, list):
                for i in file_new:
                    if '.xls' in i:
                        xls_name = i.split('\\')[-1]
                        part = MIMEApplication(open(i, 'rb').read())
                        part.add_header('Content-Disposition', 'attachment', filename=xls_name)
                        msg.attach(part)

                # jpg类型附件
                if '.jpg' in i:
                    jpg_name = i.split('\\')[-1]
                    part = MIMEApplication(open(i, 'rb').read())
                    part.add_header('Content-Disposition', 'attachment', filename=jpg_name)
                    msg.attach(part)

                if '.html' in i:
                    html_name = i.split('\\')[-1]
                    part = MIMEApplication(open(i, 'rb').read())
                    part.add_header('Content-Disposition', 'attachment', filename=html_name)
                    msg.attach(part)

                if '.json' in i:
                    json_name = i.split('\\')[-1]
                    part = MIMEApplication(open(i, 'rb').read())
                    part.add_header('Content-Disposition', 'attachment', filename=json_name)
                    msg.attach(part)

            try:
                s = smtplib.SMTP_SSL(smtp_address, smtp_port)
                s.set_debuglevel(1)
                s.login(email_address, email_password)  # 登陆服务器
                s.sendmail(email_address, _to, msg.as_string())  # 发送邮件
                s.quit()
            except Exception as e:
                logger.error('发送邮件异常{}'.format(e))
