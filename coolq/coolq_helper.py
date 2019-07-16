# -*- coding:utf-8 -*-
from http_helper import *

class CoolQHelper:
     #私聊消息需要对方先说话
     def send_private_msg(self):
        url = "http://127.0.0.1:5700/send_private_msg"
        data = {"user_id":2796228812,"message":"test22","auto_escape":False}
        do_request_json(url,data)

     def send_group_msg(self):
        url = "http://127.0.0.1:5700/send_group_msg"
        data = {"group_id": 836558712, "message": "good", "auto_escape": False}
        do_request_json(url, data)

     #讨论组不是单纯的讨论组id，需要转换,讨论组 ID（正常情况下看不到，需要从讨论组消息上报的数据中获得）
     def send_discuss_msg(self):
        url = "http://127.0.0.1:5700/send_discuss_msg"
        #data = {"discuss_id": 1520910408, "message": "[CQ:image,file=http://i1.piimg.com/567571/fdd6e7b6d93f1ef0.jpg]", "auto_escape": False}
        data = {"discuss_id": 1520910408, "message": "我是机器人小丁丁，测试讨论组的中文呢", "auto_escape": False}
        do_request_json(url, data)



     if __name__ == "__main__":
         send_private_msg(None)
         send_discuss_msg(None)
         send_group_msg(None)
