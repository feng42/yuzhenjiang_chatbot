# _*_ coding:utf-8 _*_
'''
@author:   zhangfeng
@mail:  jiangchayanjiuyuan@163.com
@date:  2020/7/17 下午2:41
@file: SessionChat.py
'''

import traceback
import tornado.web
import tornado.httpserver
from config import config_instance
from src.utils.logger import LOGGER

class SessionChatHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("please use post")

    def post(self):
        response = {
            'status': 0,
            'data': {},
            'message':'fail'
        }

