# encoding:utf-8
import base64

import requests

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from plugins import *


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



        content = e_context["context"].content
        data = {"inputs": content, "user_id": e_context["context"]["user_id"]}
        logger.info("===is facechain start ==={}".format(e_context["context"]))
        resp = ''
        if e_context["context"].type == ContextType.IMAGE:


            logger.info("===is facechain ==={}".format(e_context["context"]))
            with open(e_context["context"]["req_image_path"], 'rb') as image_file:
                image_data = image_file.read()

            files = {'image': image_data}
            resp = self.http(files, data)

        else:
            resp = self.http("", data)

        reply= process_resp(resp)

        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "我是一个写真照生成机器人,我叫agent,请对我说:\" 给我生成一个写真照 \""
        return help_text

    def http(self, files, inputs):
        if inputs == '':
            return

        if files != '':
            response = requests.post('http://region-31.seetacloud.com:25261/upload_pic', files=files, data=inputs)

        else:
            response = requests.post('http://region-31.seetacloud.com:25261/upload_pic', data=inputs)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            # 输出响应内容

            return response
        else:
            return ("请求失败，状态码:", response.status_code)

def process_resp(response):

    if "images" in response.text:
        text = json.loads(response.text)
        imgs=text['images']
        image_binarys =[]
        for index, encoded_image in enumerate(imgs):
            # 解码Base64字符串为二进制数据
            image_binary = base64.b64decode(encoded_image.encode('utf-8'))
            image_binarys.append(image_binary)

        reply = Reply()
        reply.type = ReplyType.IMAGES
        reply.content = image_binarys
        return  reply
    else:
        reply = Reply()
        reply.type = ReplyType.TEXT
        reply.content = response.text
        return reply