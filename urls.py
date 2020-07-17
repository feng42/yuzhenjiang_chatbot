from config import config_instance
from src.controller.SessionChat import SessionChatHandler

urls = [
    (r"/api/chatroom/{}".format(config_instance.VERSION),
     SessionChatHandler),
    
]
