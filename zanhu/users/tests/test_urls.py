#!/usr/bin/python3
# -*- coding: utf-8 -*-

from test_plus.test import TestCase
from django.urls import reverse, resolve


class TestUserURLs(TestCase):
    #初始化一个用户
    def setUp(self):
        self.user = self.make_user()
    # 正向向解析测试
    def test_detail_reverse(self):
        self.assertEqual(reverse('users:detail', kwargs={'username':'testuser'}), '/users/testuser/')
    # 反向解析测试
    def test_detail_resolve(self):
        self.assertEqual(resolve('/users/testuser/').view_name, 'users:detail')

    def test_update_reverse(self):
        self.assertEqual(reverse('users:update'), '/users/update/')
    def test_update_resolve(self):
        self.assertEqual(resolve('/users/update/').view_name, 'users:update')


