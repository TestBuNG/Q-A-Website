from django import forms
from zanhu.articles.models import Article

from markdownx.fields import MarkdownxFormField


class ArticleForm(forms.ModelForm):
    #在元数据中定义需要填写的字段
    status = forms.CharField(widget=forms.HiddenInput())  # 点击发表改为“P”，点击草稿改为“D”
    edited = forms.BooleanField(widget=forms.HiddenInput(), initial=False,
                                required=False)  # 在模型类中设置了默认值，所以这里initial=False
    content = MarkdownxFormField()

    class Meta:
        model = Article
        fields = ["title", "content", "image", "tags", "status", "edited"]

