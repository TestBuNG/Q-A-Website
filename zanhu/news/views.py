#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView

from zanhu.news.models import News
from django.template.loader import render_to_string   #把字段/字典渲染到前端模板
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from zanhu.helpers import ajax_required, AuthorRequireMixin

from django.urls import reverse, reverse_lazy
"""
ListView：Django通用视图
LoginRequiredMixin：登录验证
ListView类中自带的属性：queryset， paginate_by， ordering， context_object_name， page_kwarg 。。
"""

class NewsListView(LoginRequiredMixin, ListView):
    model = News #指定关联模型类，返回的是模型类中的所有对象
    paginate_by = 20 #分页数量显示,并且在url中带有?page=num
    template_name = 'news/news_list.html' #可以不写，默认为templetes-news包下："模型类名小写_list.html"


    #获取视图对象列表,默认返回django的查询集，重写可实现过滤
    def get_queryset(self):
        return News.objects.filter(reply=False)   #过滤掉回复


class NewsDeleteView(LoginRequiredMixin, AuthorRequireMixin, DeleteView):
    """DeleteView每次只能删除一条数据"""
    model = News
    template_name = 'news/news_confirm_delete.html'
   
    success_url = reverse_lazy("news:list")    #删除成功后跳转的路径 ；reverse_lazy在项目URLConf未加载前使用


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_new(request):
    """通过AJAX POST请求，发送动态"""
    post = request.POST['post'].strip()  #通过在前端定义的关键字：'post'获取POST内容
    if post:
        posted = News.objects.create(user=request.user, content=post)
        html = render_to_string('news/news_single.html', {'news':posted, 'request':request})
        #render_to_string方法渲染html模板要传递request，render不要
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest("内容不能为空！")  #返回400状态码


@login_required
@ajax_required
@require_http_methods(['POST'])
def like(request):
    """点赞， AJAX POST请求"""
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    #取消或添加赞
    news.switch_like(request.user)
    #返回点赞数量
    return JsonResponse({'likes':news.count_likers()})


@login_required
@ajax_required
@require_http_methods(["GET"])
def get_thread(request):
    """返回动态的评论，AJAX GET请求"""
    news_id = request.GET['news']
    news = News.objects.get(pk=news_id)
    news_html = render_to_string("news/news_single.html", {"news": news})  # 没有评论的时候
    thread_html = render_to_string("news/news_thread.html", {"thread": news.get_thread()})  # 有评论的时候
    return JsonResponse({
        "uuid": news_id,
        "news": news_html,
        "thread": thread_html,
    })


@login_required
@ajax_required
@require_http_methods(["POST"])
def post_comment(request):
    """评论，AJAX POST请求"""
    post = request.POST['reply'].strip()
    parent_id = request.POST['parent']   #评论的那一个动态
    parent = News.objects.get(pk=parent_id)
    if post: #若用户评论不为空
        parent.reply_this(request.user, post)
        return JsonResponse({'comments': parent.comment_count()})
    else:  # 评论为空返回400.html
        return HttpResponseBadRequest("内容不能为空！")


@login_required
@ajax_required
@require_http_methods(["POST"])
def update_interactions(request):
    """websocket自动更新评论数，点赞数"""
    data_point = request.POST['id_value']
    news = News.objects.get(pk=data_point)
    return JsonResponse({'likes': news.count_likers(), 'comments': news.comment_count()})






"""
    #定义复杂的排序方法
    def get_ordering(self):
        #把方法中的对象传递给第三方的api
        pass
    #分页的复杂逻辑
    def get_paginate_by(self, queryset):
        pass

    #添加额外的（模型类中没有的数据）上下文
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data() #重载父类方法
        context['views'] = 100
        return context   #context中包括get_queryset中过滤后的queryset以及这里的‘views’

"""
