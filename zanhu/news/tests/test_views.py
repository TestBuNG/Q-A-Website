#!/usr/bin/python3
# -*- coding: utf-8 -*-
from test_plus import TestCase
from zanhu.news.views import News
from django.test import Client    #客户端发送请求的方式测试View
from django.urls import reverse


class NewsViewTest(TestCase):
    #测试场景准备
    def setUp(self):
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        self.client = Client()
        self.other_client = Client()

        self.client.login(username='user01', password='password')
        self.other_client.login(username='user02', password='password')

        self.first_news = News.objects.create(
            user=self.user,
            content="第一条动态"
        )
        self.second_news = News.objects.create(
            user=self.user,
            content="第二条动态"
        )

        self.reply_first_news = News.objects.create(
            user=self.other_user,
            content='评论第一条动态',
            reply=True,
            parent=self.first_news
        )

    #测试动态列表页功能
    def test_news_list(self):
        response = self.client.get(reverse("news:list"))
        self.assertEquals(response.status_code, 200)
        #assert response.status_code == 200
        assert self.first_news in response.context['news_list'] #通过字典的方式获取指定的上下文
        assert self.second_news in response.context['news_list']
        assert self.reply_first_news not in response.context['news_list']

    #测试删除动态
    def test_delete_news(self):
        initial_count = News.objects.count()
        response = self.client.post(
            reverse("news:delete_news", kwargs={"pk":self.second_news.pk})
        )
        assert response.status_code == 302
        assert News.objects.count() == initial_count - 1

    #测试发送动态
    def test_post_news(self):
        initial_count = News.objects.count()
        response = self.client.post(
            reverse("news:post_news"),
            {"post":"发送动态"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest" )#发送http ajax请求

        assert response.status_code == 200
        assert News.objects.count() == initial_count + 1

    #点赞
    def test_like_news(self):
        response = self.client.post(
            reverse("news:like_post"),
            {"news":self.first_news.pk},  #让user01给自己的动态点赞
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code ==200
        assert self.first_news.count_likers() == 1
        assert self.user in self.first_news.get_likers()  #用户1在点赞用户中
        assert response.json()["likes"] == 1

    #获取动态的评论
    def test_get_thread(self):
        response =self.client.get(
            reverse("news:get_thread"),
            {"news":self.first_news.pk},
        HTTP_X_REQUESTED_WITH = "XMLHttpRequest"
        )

        assert response.status_code == 200
        assert response.json()["uuid"] == str(self.first_news.pk)
        assert "第一条动态" in response.json()["news"]
        assert "评论第一条动态" in response.json()["thread"]

    #发表评论
    def test_post_comments(self):
        response = self.client.post(
            reverse("news:post_comment"),
            {"reply": "评论第二条动态", "parent":self.second_news.pk},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        assert response.status_code == 200
        assert response.json()["comments"] == 1







