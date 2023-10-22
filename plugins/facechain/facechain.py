# encoding:utf-8
import json

import PIL
import requests
from PIL import Image

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from cachetools import TTLCache


@plugins.register(
    name="Facechain",
    desire_priority=100000,
    hidden=True,
    desc="facechain agent",
    version="0.1",
    author="William",
)
class Facechain(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Hello] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
            ContextType.IMAGE,
            ContextType.JOIN_GROUP,
            ContextType.PATPAT,
        ]:
            return

        reply = Reply()
        reply.type = ReplyType.TEXT

        content = e_context["context"].content
        user_id = "1212121221"
        data = {"inputs": content, "user_id": user_id}

        if e_context["context"].type == ContextType.IMAGE:
            resp = ''
            # with open("D:\\PycharmProjects\\chatgpt-on-wechat\\tmp\\1.png", 'rb') as image_file:
            logger.info("content :", e_context["context"].content)
            with open(e_context["context"].content, 'rb') as image_file:
                files = {'image': image_file}
                resp = self.http(files, data)

        else:
            resp = self.http("", data)

        reply.content = resp
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "我是一个写真照生成机器人,我叫agent,请对我说:\" 给我生成一个写真照 \""
        return help_text

    def http(self, files, inputs):
        if inputs == '':
            return

        if files != '':
            response = requests.post('http://127.0.0.1:8080/upload_pic', files=files, data=inputs)

        else:
            response = requests.post('http://127.0.0.1:8080/upload_pic', data=inputs)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            # 输出响应内容
            return (response.text)
        else:
            return ("请求失败，状态码:", response.status_code)

#
# cache = TTLCache(maxsize=100, ttl=600)  # 缓存最多100个项，每个项的过期时间为60秒
#
#
# def build_req(context, user_id):
#     # 创建一个支持过期时间的缓存
#     if cache.get(user_id) is not None:
#         chatbot = cache.get(user_id)[1]
#         chatbot.append((context, None))
#         req = [context, chatbot]
#     else:
#         chatbot = (context, None)
#         req = [context, chatbot]
#     return req
#
#
# def save_history(context, resp, user_id):
#     his = cache.get(user_id)
#     if his is None:
#         chatbot = (context, resp)
#         newMsg = ["", [chatbot]]
#         cache[user_id] = newMsg
#     else:
#         chatbot = his[1]
#         chatbot[-1] = (context, resp)
#         cache[user_id] = his
#     print(cache[user_id])
