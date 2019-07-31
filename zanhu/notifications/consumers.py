#!/usr/bin/python3
# -*- coding:utf-8 -*-

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationsConsumer(AsyncWebsocketConsumer):
    """处理通知应用中的websocket请求"""
    async def connect(self):
        """（一）建立连接"""
        # 1.验证用户身份
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            #1.1若用户已登录，让这个用户监听频道上的“消息通知”的组。首先将用户加入到该组里。
            """'notifications'这里是固定的组名，与messager的不同，它接收的是全局消息，
            但可在视图中控制（只把对应的通知传递给reseive函数）
            """
            # 1.1.1 channel_layer:获取频道层,group_add('组名', '频道名'):加到组中
            await self.channel_layer.group_add('notifications', self.channel_name)
            await self.accept() #1.1.2接受连接

    async def receive(self, text_data=None, bytes_data=None):
        """（二）将接受到的后端数据（视图中的group_send中的数据）推送给前端"""
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """（三）断开连接"""
        await self.channel_layer.group_discard('notifications', self.channel_name)

