#!/usr/bin/python3
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from slugify import slugify
from taggit.managers import TaggableManager 

@python_2_unicode_compatible
class ArticleQuerySet(models.query. QuerySet):
    """自定义QuerySet（查询集），提高模型类的可用性"""
    def get_published(self):
        """获取已发表的文章"""
        return self.filter(status="P")

    def get_drafts(self):
        """获取已发表的文章"""
        return self.filter(status="D")

    def get_counted_tags(self):
        """
        统计所有已发表的文章中，每一个标签的名称及数量（大于0的）
        annotate：聚合查询
        tags__gt=0：大于0的tags
        """
        tag_dict = {}
        query = self.get_published().annotate(tagged=models.Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()   


@python_2_unicode_compatible
class Article(models.Model):

    STATUS = (("D", "Draft"), ("P", "Published"))
    title = models.CharField(max_length=255, null=False, unique=True, verbose_name='标题')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="author", on_delete=models.SET_NULL, verbose_name='作者')
    image = models.ImageField(upload_to='articles_pictures/%Y/%m/%d/', verbose_name='文章图片')
    slug = models.SlugField(max_length=80, null=True, blank=True, verbose_name='(URL)别名')  #slug: 标识不同的url，url后缀
    status = models.CharField(max_length=1, choices=STATUS, default='D', verbose_name='状态')  # choice=草稿 or 已发表
    content = MarkdownxField(verbose_name='内容')
    edited = models.BooleanField(default=False, verbose_name='是否可编辑')
    tags = TaggableManager(help_text='多个标签使用,(英文)隔开', verbose_name='标签')  #help_text：说明
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    objects = ArticleQuerySet.as_manager()  #在模型类中关联编写好的自定义查询集

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ("created_at",)

    def __str__(self):
        return self.title

    #用户在保存文章时自动生成slug
    """重写save()方法"""
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.title)
        super(Article, self).save() #重载父类方法

    def get_markdown(self):
        """将markdown文本转换为Html格式"""
        return markdownify(self.content)

