# -*- coding: utf-8 -*-#
import os

import requests

from bridge.context import ContextType
from channel.chat_message import ChatMessage
from common.log import logger
from common.tmp_dir import TmpDir


class WeChatMPMessage(ChatMessage):
    def __init__(self, msg, client=None):
        super().__init__(msg)
        self.msg_id = msg.id
        self.create_time = msg.time
        self.is_group = False
        self.req_image_path =""
        if msg.type == "text":
            self.ctype = ContextType.TEXT
            self.content = msg.content
        elif msg.type == "voice":
            if msg.recognition == None:
                self.ctype = ContextType.VOICE
                self.content = TmpDir().path() + msg.media_id + "." + msg.format  # content直接存临时目录路径

                def download_voice():
                    # 如果响应状态码是200，则将响应内容写入本地文件
                    response = client.media.download(msg.media_id)
                    if response.status_code == 200:
                        with open(self.content, "wb") as f:
                            f.write(response.content)
                    else:
                        logger.info(f"[wechatmp] Failed to download voice file, {response.content}")

                self._prepare_fn = download_voice
            else:
                self.ctype = ContextType.TEXT
                self.content = msg.recognition
        elif msg.type == "image":
            logger.info("===is image ===")
            self.ctype = ContextType.IMAGE
         #   self.content = TmpDir().path() + msg.media_id + ".png"  # content直接存临时目录路径
            

            
            
            def download_req_pic(image_url):

                # 指定保存图片的文件夹路径
                download_folder = TmpDir().path() + msg.media_id + "req" + ".png"

                # 确保保存文件夹存在
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)

                # 从链接中提取文件名
                image_filename = os.path.join(download_folder, os.path.basename(image_url))

                # 发起 HTTP GET 请求
                response = requests.get(image_url)

                if response.status_code == 200:
                    # 如果请求成功，将图片数据保存到文件夹
                    with open(image_filename, "wb") as file:
                        file.write(response.content)

                    print(f"图片已下载到：{image_filename}")
                    self.req_image_path = image_filename
                else:
                    print("图片下载失败，状态码:", response.status_code)

            download_req_pic(msg.image)

            self.content = TmpDir().path() + msg.media_id + ".png"  # content直接存临时目录路径

            def download_image():
                # 如果响应状态码是200，则将响应内容写入本地文件
                response = client.media.download(msg.media_id)
                if response.status_code == 200:
                    with open(self.content, "wb") as f:
                        f.write(response.content)
                else:
                    logger.info(f"[wechatmp] Failed to download image file, {response.content}")

            self._prepare_fn = download_image
        else:
            raise NotImplementedError("Unsupported message type: Type:{} ".format(msg.type))

        self.from_user_id = msg.source
        self.to_user_id = msg.target
        self.other_user_id = msg.source
