# _*_ coding:utf-8 _*_
'''
@author:   zhangfeng
@mail:  jiangchayanjiuyuan@163.com
@date:  2020/7/17 上午11:06
@file: config.py
'''
import os

class Config:
    def __init__(self):
        self.service_name = 'jzy-chatbot-server'
        self.VERSION = 'v1'
        self.process_num = 1
        self.port = 10008


        # keeper
        self.num_keepers = 20



        # log
        self.log_name = 'jzy-chatbot-server'
        self.log_level = 'debug'
        self.log_dir = 'logs/'

        self.server_name = 'prod'


class ModelConfig():
    def __init__(self):
        self.device = '0' # gpu设备号
        self.use_cuda = True

        self.temperature = 1 # 生成温度
        self.topk = 8 # topk
        self.topp = 0 # topp
        self.repetition_penalty = 1.0
        self.seed = None

        self.max_len = 25
        self.max_history_len = 5
        self.batch_size = 5

        self.model_config = 'models/GPT2Chatbot/model_config_dialogue_small.json'  # 模型超参数
        self.vocab_path = 'models/GPT2Chatbot/vocab_small.txt'  # 模型词库
        self.dialogue_model_path = 'models/GPT2Chatbot/dialogue_model/'  # dialogue路径
        self.mmi_model_path = 'models/GPT2Chatbot/mmi_model/'  # mmi路径

        self.log_path = 'logs/interacting_mmi.log'
        self.save_samples_path = 'sample/'

        self.debug = True

        # session history
        self.history_path = 'data/history/'
        if not os.path.exists(self.history_path):
            os.makedirs(self.history_path)
        self.expire_path = 'data/expire/'
        if not os.path.exists(self.expire_path):
            os.makedirs(self.expire_path)
        self.num_keepers = 20


config_instance = Config()
config_model = ModelConfig()

if __name__ == '__main__':
    config_instance = Config()