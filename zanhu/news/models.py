#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models

import uuid
from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from zanhu.notifications.views import notification_handler


@python_2_unicode_compatible
class News(models.Model):
    """
    uuid.uuid4:用这种方法自动生成uuid,
    editable=False : 不允许编辑
    """
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name='publisher', verbose_name='用户')
    #动态和动态评论存在一张表里，所以用自关联
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE,
                               related_name='thread', verbose_name='自关联')
    content = models.TextField(verbose_name='动态内容')
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_news', verbose_name='点赞用户')
    reply = models.BooleanField(default=False, verbose_name='是否为评论')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间') #db_index=True：加速查找
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '首页'
        verbose_name_plural= verbose_name
        ordering = ("-created_at",)

    def __str__(self): #展示模型对象直观的信息
        return self.content

    #点/取消赞函数
    def switch_like(self, user):
        #若用户已经点赞，则取消点赞
        if user in self.liked.all():
            self.liked.remove(user)
        #若用户没有点赞则点赞
        else:
            self.liked.add(user)
            #通知楼主
            notification_handler(user, self.user, 'L', self, id_value=str(self.uuid_id), key='social_update')

    #返回自关联的上级记录或本身
    def get_parent(self):
        if self.parent:
            return self.parent
        #若当前实例不是评论，是用户发表的状态，就返回本身self
        else:
            return self

    #回复首页动态
    """user:登录的用户，text:回复的内容"""
    def reply_this(self, user, text):
        #获取父级记录
        parent = self.get_parent()
        News.objects.create(
            user=user,
            reply=True,
            parent=parent,
            content=text,
        )
        notification_handler(user, parent.user, 'R', parent, id_value=str(parent.uuid_id), key='social_update')

    #获取关联到当前记录的所有记录
    def get_thread(self):
        parent = self.get_parent()
        # 可以通过related_name来反向查询子表中关联到父表的某一条数据的子表数据
        # 这里是子关联表，可以通过父记录，查到所有子记录
        return parent.thread.all()


    #获取评论数就是获取关联到当前记录的所有记录
    def comment_count(self):
        return self.get_thread().count()

    #获取点赞数
    def count_likers(self):
        return self.liked.count()

    #获取所有点赞用户
    def get_likers(self):
        return self.liked.all()

    #有用户发表动态则通知全部在线用户
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(News, self).save()
        if not self.reply:
            channel_layer = get_channel_layer()
            payload = {
                'type': 'receive',
                'key': 'additional_news',
                'actor_name': self.user.username,
            }
            async_to_sync(channel_layer.group_send)('notifications', payload)
