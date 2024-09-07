from django.db import models
from django.contrib.auth import get_user_model

class ArticleTag(models.Model):
    slug = models.CharField(verbose_name='SLUG', unique=True, max_length=20, primary_key=True)
    name = models.CharField(verbose_name='タグ名', unique=True, max_length=20)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'タグ'
        db_table = 'article_tag'

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(verbose_name='タイトル', default='タイトルです。', max_length=30, null=False, blank=False)
    text = models.TextField(verbose_name='テキスト', default='テキストです。', max_length=255, null=False, blank=False)
    author = models.ForeignKey(get_user_model(), verbose_name='作成者', on_delete=models.CASCADE)
    tags = models.ManyToManyField(ArticleTag, verbose_name='タグ', related_name='articles')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '記事'
        db_table = 'article'

    def __str__(self):
        return self.title

class Comment(models.Model):
    comment = models.TextField(verbose_name='コメント', max_length='500')
    user = models.ForeignKey(get_user_model(), verbose_name='投稿者', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'コメント'
        db_table = 'comment'

    def __str__(self):
        return self.comment


class ArticleLike(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name='投稿者', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, related_name='article_like')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'いいね'
        db_table = 'article_like'

    def __str__(self):
        return f'{ self.user } : {self.article}'