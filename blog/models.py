from django.db import models
from django.contrib.auth import get_user_model

class Article(models.Model):
    title = models.CharField(verbose_name='タイトル', default='タイトルです。', max_length=30, null=False, blank=False)
    text = models.TextField(verbose_name='テキスト', default='テキストです。', max_length=255, null=False, blank=False)
    author = models.CharField(verbose_name='作成者', max_length=50, null=False, blank=False)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)


class Comment(models.Model):
    comment = models.TextField(verbose_name='コメント', max_length='500')
    user = models.ForeignKey(get_user_model(), verbose_name='投稿者', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
