#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/11/17 11:25
# @Author : LiZongJie
# @Site : 
# @File : DingTalkRobot.py
# @Software: PyCharm
import time
import requests
# import dataframe_image as dfi
# from dingtalkchatbot.chatbot import DingtalkChatbot

'''
sendDingTalkText：发送文本
sendDingTalkImage：发送图片
sendDingTalkLink：发送连接
sendDingTalkMarkdown：发送图片和文本
generate_images:生成table图片
upload_image:上传图片获取图片路径
'''


class DingTalkRobot(object):
    def __init__(self, file_name=None):
        self.send_date = time.strftime('%Y-%m-%d')
        self.now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        if file_name:
            self.file_name = f"{file_name}.png"
        else:
            self.file_name = "{}.png".format(int(time.time()))

    def sendDingTalkText(self, webhook, text, at_mobiles):
        '''
        发送一般文本信息
        :param accesskey: 机器人
        :param text: 文本内容
        :param at_mobiles: 需要@手机号
        :return:
        '''
        # webhook = "https://oapi.dingtalk.com/robot/send?access_token=%s" % (accesskey)
        xiaoding = DingtalkChatbot(webhook)
        xiaoding.send_text(msg='{text}'.format(text=text), at_mobiles=at_mobiles)

    def sendDingTalkImage(self, webhook, pic_url):
        '''
        发送一张图片
        :param accesskey: 机器人
        :param pic_url: 图片地址
        :return:
        '''
        # webhook = "https://oapi.dingtalk.com/robot/send?access_token=%s" % (accesskey)
        xiaoding = DingtalkChatbot(webhook)
        xiaoding.send_image(pic_url='{pic_url}'.format(pic_url=pic_url))

    def sendDingTalkLink(self, webhook, title, text, message_url, pic_url):
        '''
        发送Link消息
        :param accesskey: 机器人
        :param title: 标题包含机器人关键字
        :param text: 文本
        :param message_url: 连接地址
        :param pic_url: 图片地址
        :return:
        '''
        # webhook = "https://oapi.dingtalk.com/robot/send?access_token=%s" % (accesskey)
        xiaoding = DingtalkChatbot(webhook)
        xiaoding.send_link(title=f'{title}', text=f'{text}', message_url=f'{message_url},pic_url={pic_url}')

    def sendDingTalkMarkdown(self, webhook, title, head, top_message, file, follow_message, at_mobiles):
        '''
        发送图片和文本结合的信息
        :param accesskey:机器人
        :param title:标题
        :param head:头部
        :param top_message:首行
        :param file:图片文件
        :param follow_message:尾行
        :param at_mobiles: at_mobiles为True,为@所有人，
        :return:
        '''
        # webhook = "https://oapi.dingtalk.com/robot/send?access_token=%s" % (accesskey)
        xiaoding = DingtalkChatbot(webhook)
        xiaoding.send_markdown(title=f'{title}', text='#### **{head}**\n'
                                                      '> {top_message}\n\n'
                                                      ' ![内容]({file})\n'
                                                      '> ###### {follow_message} \n'.format(head=head,
                                                                                            top_message=top_message,
                                                                                            file=file,
                                                                                            follow_message=follow_message),
                               at_mobiles=at_mobiles
                               )

    def sendDingTalkMarkdownNotImg(self, webhook, title, head, top_message, message, follow_message, at_mobiles):
        '''
        发送文本信息
        :param accesskey:机器人
        :param title:标题
        :param head:头部
        :param top_message:首行
        :param message:主题内容
        :param follow_message:尾行
        :param at_mobiles: at_mobiles为True,为@所有人，
        :return:
        '''
        # webhooks = webhook
        # webhook = "https://oapi.dingtalk.com/robot/send?access_token=%s" % (accesskey)
        xiaoding = DingtalkChatbot(webhook)
        xiaoding.send_markdown(title=f'{title}', text='#### **{head}**\n'
                                                      '> {top_message}\n\n'
                                                      '{message}\n\n'
                                                      '> ###### {follow_message} \n'.format(head=head,
                                                                                            top_message=top_message,
                                                                                            message=message,
                                                                                            follow_message=follow_message),
                               at_mobiles=at_mobiles
                               )

    def generate_images(self, df):
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['simhei']
        dfi.export(df, self.file_name, table_conversion='matplotlib',max_rows=200)

    def upload_image(self):
        '''
        上传图片在oss平台，获取图片地址
        :return:
        '''
        url = 'https://nczupload.carzone365.com/api/v1/public/upload/object/batch'
        files = {'file': open(self.file_name, 'rb')}
        data = {'file': files}
        result = requests.post(url, data, files=files)
        request_image = result.json()
        file = request_image['data'][0]
        print(file)
        return file
