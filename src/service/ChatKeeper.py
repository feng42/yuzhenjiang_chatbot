# _*_ coding:utf-8 _*_
'''
@author:   zhangfeng
@mail:  jiangchayanjiuyuan@163.com
@date:  2020/7/17 下午3:50
@file: ChatKeeper.py
'''

import time
import json
import threading
import traceback
from config import config_model
from src.utils.logger import LOGGER

class ChatKeeperThread(threading.Thread):
    def __init__(self, partition_index):
        threading.Thread.__init__(self)
        self.keeper_index = partition_index
        self.history_save_path = config_model.history_path + 'part-{}.json'.format(partition_index)
        self.expire_save_path = config_model.expire_path + 'part-{}.log'.format(partition_index)
        self.history_dict = {}
        self.max_history_len = config_model.max_history_len

    def run(self):
        while True:
            time.sleep(1800)
            cur_update_time = time.time()
            expire_list = []

            for key in self.history_dict.keys():
                try:
                    if not "history" in self.history_dict[key]:
                        self.history_dict.pop(key)
                        expire_list.append(json.dumps({
                            "session_id":key,
                            "history":[],
                            "last_modified":time.time() - 1800
                        }))
                    if "modified_time" in self.history_dict[key] and type(self.history_dict[key]["modified_time"]) == float:
                        if cur_update_time - self.history_dict[key]["modified_time"] > 1800:
                            self.history_dict.pop(key)
                            expire_list.append(json.dumps({
                                "session_id":key,
                                "history": self.history_dict[key]["history"],
                                "last_modified": self.history_dict[key]["modified_time"]
                            }))
                    else:
                        self.history_dict.pop(key)
                        expire_list.append(json.dumps({
                                "session_id":key,
                                "history": self.history_dict[key]["history"],
                                "last_modified": time.time() - 1800
                        }))
                except Exception as e:
                    LOGGER.error("bad exec: {}, reason: {}".format(str(key),str(e)))
                    traceback.print_exc()
                    continue


            with open(self.expire_save_path, 'a') as fw:
                for expire_session in expire_list:
                    fw.write(expire_session+'\n')

            with open(self.history_save_path, 'w') as fw:
                json.dump(self.history_dict,fw)

    def update_history(self,session_id, new_input_text):
        try:
            if session_id not in self.history_dict:
                self.history_dict[session_id] = {
                    "history": [],
                    "modified_time": time.time()
                }
            self.history_dict[session_id]["history"].append(new_input_text)
            self.history_dict[session_id]["modified"] = time.time()
            return True
        except Exception as e:
            LOGGER.error("FAIL update history: session_id: {}, error: {}".format(str(session_id), str(e)))
            return False

    def get_history(self,session_id):
        try:
            if session_id not in self.history_dict or "history" not in self.history_dict[session_id]:
                return []
            else:
                return self.history_dict[session_id]["history"][-self.max_history_len:]
        except Exception as e:
            LOGGER.error("FAIL update history: session_id: {}, error: {}".format(str(session_id), str(e)))
            return []

keepers = {}
for keeper_index in range(config_model.num_keepers):
    keepers[keeper_index] = ChatKeeperThread(keeper_index)
    keepers[keeper_index].start()






