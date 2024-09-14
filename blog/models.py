import os

from typing import Any
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

CHARGE_TYPE = (
    (0, '課金なし'),
    (1, 'クレジットカード決済'),
)

def upload_article_image_to(instance, filename):
    user_id = str(instance.user.id)
    return os.path.join('article', 'images', user_id, filename)


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


class Image(models.Model):
    image = models.ImageField(verbose_name='投稿画像', upload_to=upload_article_image_to)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '投稿画像'
        db_table = 'article_image'


class Article(models.Model):
    title = models.CharField(verbose_name='タイトル', default='タイトルです。', max_length=30, null=False, blank=False)
    images = models.ForeignKey(Image, verbose_name="投稿画像", on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField(verbose_name='テキスト', default='テキストです。', max_length=255, null=False, blank=False)
    author = models.ForeignKey(get_user_model(), verbose_name='作成者', on_delete=models.CASCADE, related_name='articles')
    tags = models.ManyToManyField(ArticleTag, verbose_name='タグ', related_name='articles')
    is_public = models.BooleanField(verbose_name='公開', default=False)
    sell_flag = models.BooleanField(verbose_name='記事を販売', default=False)
    price = models.IntegerField(verbose_name='価格', default=0, blank=True, null=True)
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


class Order(models.Model):

    ORDER_STATUS = (
        (0, '決済未登録'),
        (1, '決済完了'),
        (2, '決済失敗'),
        (200, '決済取り消し'),
    )

    user = models.ForeignKey(get_user_model(), verbose_name='ユーザー', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, related_name='order')
    price = models.IntegerField(verbose_name='価格', blank=True, null=True)
    charge_type = models.SmallIntegerField(verbose_name='課金タイプ', choices=CHARGE_TYPE, default=1)
    order_status = models.SmallIntegerField(verbose_name='決済ステータス', choices=ORDER_STATUS, default=1)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'ユーザー注文履歴'
        db_table = 'order'


class UserItem(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name='ユーザー', on_delete=models.CASCADE, related_name='user_item')
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, related_name='user_item')
    charge_type = models.SmallIntegerField(verbose_name='課金タイプ', choices=CHARGE_TYPE, default=1)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta():
        verbose_name_plural = 'ユーザー購入商品'
        unique_together = ('user', 'article')
        db_table = 'user_item'

class ViewCount(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name='ユーザー', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, related_name='view_count')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '記事の閲覧カウント'
        db_table = 'view_count'
        indexes = [
            models.Index(fields=['article', 'created_at']),
        ]

    @classmethod
    def create_view_count(cls, user, article):
        if user != article.author:
            # 存在していなかったら新規で作成し、存在していたらレコードを返す
            cls.objects.get_or_create(user=user, article=article)
        view_count = cls.objects.filter(article=article).count()
        return view_count


class Follow(models.Model):
    follower = models.ForeignKey(get_user_model(), verbose_name="フォローしたユーザー", related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(get_user_model(), verbose_name="フォローされたユーザー", related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name_plural = 'フォロー'
        db_table = 'user_follow'
        unique_together = ('follower', 'followed')

    # def __init__(self):
    #     return f'{self.follower} follows {self.followed}'