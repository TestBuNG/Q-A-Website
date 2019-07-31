#!/usr/bin/python3
# -*- coding:utf-8 -*-

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessagesConsumer(AsyncWebsocketConsumer):
    """处理私信websocket请求"""
    async def connect(self):
        if self.scope['user'].is_anonymous:
             #未登录的用户拒绝连接
             await self.close()
        else:
             """加入聊天组到监听频道"""
             #channel_layer:获取监听频道
             #group_add（组名，监听频道）：用登录的用户名命名新建组
             #channel_name：自动生成频道名
             await self.channel_layer.group_add(self.scope['user'].username, self.channel_name)
             await self.accept()  #建立连接

    async def receive(self, text_data=None, bytes_data=None):
        #"""接受私信，推送到前端"""
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
         """离开聊天组"""
         await self.channel_layer.group_discard(self.scope['user'].username, self.channel_name)
