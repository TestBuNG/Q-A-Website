#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.http import HttpResponseBadRequest
from functools import wraps

from django.views.generic import View
from django.core.exceptions import PermissionDenied


def ajax_required(f):  #f为要装饰的函数
    """验证是否为ajax请求"""

    @wraps(f)      # @wraps()装饰的函数不会在执行后改变传入的f的名称信息
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():  #request.is_ajax()判断是否为ajax请求
            return HttpResponseBadRequest('不是AJAX请求！')
        return f(request, *args, **kwargs)
    return wrap


class AuthorRequireMixin(View): #类名表示它是多继承的
    """验证是否为原作者，用于动态删除及后面的文章编辑"""
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().user.username != self.request.user.username:
            raise PermissionDenied
        #若对象中的用户是登录用户的话，则直接重载父类的方法返回
        return super().dispatch(request, *args, **kwargs)
