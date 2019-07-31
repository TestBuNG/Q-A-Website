#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from zanhu.articles.models import Article
from zanhu.articles.forms import ArticleForm
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from zanhu.helpers import AuthorRequireMixin

from django_comments.signals import comment_was_posted
from zanhu.notifications.views import notification_handler
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class ArticlesListView(LoginRequiredMixin, ListView):
    """已发布的文章列表页"""
    model = Article
    paginate_by = 10
    context_object_name = "articles"  #上下文名字前端模板中写的是"articles"
    template_name = 'articles/article_list.html'

    #在列表页的右侧添加了文章的标签云，因此需要添加额外的上下文
    #get_context_data可以用于给模板传递模型以外的内容或参数
    def get_context_data(self, *args, **kwargs):
        #首先重载父类的方法
        context = super().get_context_data(*args, **kwargs)
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    #重写get_queryset方法，只返回已发布的文章
    def get_queryset(self, **kwargs):
        return Article.objects.get_published()


class DraftListView(ArticlesListView):
    """获取草稿箱文章列表"""
    def get_queryset(self, **kwargs):
        """获取当前用户的草稿"""
        return Article.objects.filter(user=self.request.user).get_drafts()


@method_decorator(cache_page(60 * 60), name='get')
#表示将这个类的get方法缓存1小时，注：get只能小写
class ArticleCreateView(LoginRequiredMixin, CreateView):
    """发表文章"""
    model = Article
    form_class = ArticleForm  #关联表单
    template_name = "articles/article_create.html"
    message = "文章创建成功！"  #定义消息内容

    def form_valid(self, form):
        #将登录的用户传递给表单实例
        form.instance.user = self.request.user
        return super(ArticleCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message) #消息机制messages:将某个地方定义的消息传递给下一次请求
        return reverse_lazy("articles:list")


class ArticleDetailView(LoginRequiredMixin, DetailView):
    """文章详情"""
    model = Article
    template_name = 'articles/article_detail.html'


class ArticleEditView(LoginRequiredMixin, AuthorRequireMixin, UpdateView):
    """编辑文章"""
    model = Article
    message = "文章编辑成功！"
    form_class = ArticleForm
    template_name = 'articles/article_update.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArticleEditView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('articles:article', kwargs={"slug": self.get_object().slug})


def notify_comment(**kwargs):
    """文章有评论时通知作者"""
    actor = kwargs['request'].user
    obj = kwargs['comment'].content_object

    notification_handler(actor, obj.user, 'C', obj)

comment_was_posted.connect(receiver=notify_comment)
