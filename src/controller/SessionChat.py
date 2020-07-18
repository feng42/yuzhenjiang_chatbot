# _*_ coding:utf-8 _*_
'''
@author:   zhangfeng
@mail:  jiangchayanjiuyuan@163.com
@date:  2020/7/17 下午2:41
@file: SessionChat.py
'''

import json
import time
import traceback
import tornado.web
import tornado.httpserver
from config import config_instance
from src.utils.logger import LOGGER
from src.service.ChatKeeper import keepers
from src.service.ChatWorker import worker

class SessionChatHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("please use post")

    def post(self):
        response = {
            'status': 0,
            'data': {},
            'message':'fail'
        }
        try:
            session_id = self.get_argument("sessionId")
            input_text = self.get_argument("text")
        except Exception as e:
            LOGGER.error("FAIL receive args: {}".format(str(e)))
            response['message'] = str(e)
            self.finish(response)
            return

        try:
            st = time.time()
            session_id = int(session_id)
            keeper_partition = session_id % config_instance.num_keepers
            keepers[keeper_partition].update_history(session_id=session_id,new_input_text=input_text)
            history = keepers[keeper_partition].get_history(session_id=session_id)
            generate_chars = worker.generate(input_text,history)
            print(generate_chars)
            if len(generate_chars) == 0:
                response['message'] = "fail generate response text"
                self.finish(response)
            generate = "".join(generate_chars)
            keepers[keeper_partition].update_history(session_id=session_id, new_input_text=generate)
            body_info = {
                'sessionId': session_id,
                'input': input_text,
                'output': generate
            }
            print(body_info)
            LOGGER.info("receive: session_id: {}, input_text: {}, back: {}".format(str(session_id),input_text,json.dumps(body_info)))
            response['data'] = body_info
            response['status'] = 1
            response['message'] = 'success'
            self.finish(response)

        except Exception as e:
            LOGGER.error("FAIL make resonse: {}".format(str(e)))
            response['message'] = str(e)
            self.finish(response)
        return



