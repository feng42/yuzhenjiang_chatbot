# _*_ coding:utf-8 _*_
'''
@author:   zhangfeng
@mail:  jiangchayanjiuyuan@163.com
@date:  2020/7/17 下午2:29
@file: run_server.py
'''

import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import argparse
from src.utils.logger import LOGGER

from tornado.options import define, options


from config import config_instance
from urls import urls

def main(args):

    LOGGER.info('start')

    app = tornado.web.Application(
            handlers=urls,
            debug=False)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(args.port)
    http_server.start(args.threads)

    #http_server.listen(options.port)
    print("START")
    tornado.ioloop.IOLoop.instance().start()
    print("INSTANT START")

if __name__ == "__main__":
    os.environ['CUDA_VISIBLE_DEVICES'] = '3'
    parse = argparse.ArgumentParser()
    parse.add_argument('--port',type=int, default=config_instance.port)
    parse.add_argument('--threads', type=int, default=config_instance.process_num)
    main(parse.parse_args())