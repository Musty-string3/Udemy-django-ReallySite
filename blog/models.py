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
    user_id = 'UserID:' + str(instance.article.author.id)
    article_id = 'ArticleID:' + str( instance.article.id)
    return os.path.join('article', 'images', user_id, article_id, filename)


def upload_dm_image_to(instance, filename):
    user_id = 'UserID:' + str(instance.message.sender.id)
    return os.path.join('dm', 'images', user_id, filename)


class ArticleTag(models.Model):
    slug = models.CharField(verbose_name='SLUG', unique=True, max_length=20, primary_key=True)
    name = models.CharField(verbose_name='タグ名', unique=True, max_length=20, db_index=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '01-03.タグ'
        db_table = 'article_tag'

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(verbose_name='タイトル', default='タイトルです。', max_length=30, null=False, blank=False)
    text = models.TextField(verbose_name='テキスト', default='テキストです。', max_length=255, null=False, blank=False)
    author = models.ForeignKey(get_user_model(), verbose_name='作成者', on_delete=models.CASCADE, db_index=True, related_name='articles')
    tags = models.ManyToManyField(ArticleTag, verbose_name='タグ', related_name='articles')
    is_public = models.BooleanField(verbose_name='公開', default=False)
    sell_flag = models.BooleanField(verbose_name='記事を販売', default=False)
    price = models.IntegerField(verbose_name='価格', default=0, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '01-01.記事'
        db_table = 'article'

    def __str__(self):
        return self.title



class Image(models.Model):
    image = models.ImageField(verbose_name='投稿画像', upload_to=upload_article_image_to)
    article = models.ForeignKey(Article, verbose_name="記事", on_delete=models.CASCADE, default='', related_name='image', db_index=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)


    class Meta:
        verbose_name_plural = '01-02.投稿画像'
        db_table = 'article_image'



class Comment(models.Model):
    comment = models.TextField(verbose_name='コメント', max_length='500')
    user = models.ForeignKey(get_user_model(), verbose_name='投稿者', on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, db_index=True ,related_name='comments')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '02-02.コメント'
        db_table = 'comment'

    def __str__(self):
        return self.comment


class ArticleLike(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name='投稿者', on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, db_index=True, related_name='article_like')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '02-01.いいね'
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

    user = models.ForeignKey(get_user_model(), verbose_name='ユーザー', on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, db_index=True, related_name='order')
    price = models.IntegerField(verbose_name='価格', blank=True, null=True)
    charge_type = models.SmallIntegerField(verbose_name='課金タイプ', choices=CHARGE_TYPE, default=1)
    order_status = models.SmallIntegerField(verbose_name='決済ステータス', choices=ORDER_STATUS, default=1)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '12-01.ユーザー注文履歴'
        db_table = 'order'


class UserItem(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name='ユーザー', on_delete=models.CASCADE, db_index=True, related_name='user_item')
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, db_index=True, related_name='user_item')
    charge_type = models.SmallIntegerField(verbose_name='課金タイプ', choices=CHARGE_TYPE, default=1)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta():
        verbose_name_plural = '04-02.ユーザー購入商品'
        unique_together = ('user', 'article')
        db_table = 'user_item'

class ViewCount(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name='ユーザー', on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(Article, verbose_name='記事', on_delete=models.CASCADE, db_index=True, related_name='view_count')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = '02-03.記事の閲覧カウント'
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
    follower = models.ForeignKey(get_user_model(), verbose_name="フォローしたユーザー", related_name='following', on_delete=models.CASCADE, db_index=True)
    followed = models.ForeignKey(get_user_model(), verbose_name="フォローされたユーザー", related_name='followers', on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name_plural = '03-01.フォロー'
        db_table = 'user_follow'
        unique_together = ('follower', 'followed')



ACTION_TYPE = (
    ('new_registration', 'New_registration'),
    ('comment', 'Comment'),
    ('like', 'Like'),
    ('follow', 'Follow'),
    ('purchase', 'Purchase'),
)


class Conversation(models.Model):
    user1 = models.ForeignKey(get_user_model(), verbose_name="ユーザー1", on_delete=models.CASCADE, related_name="conversation_user1")
    user2 = models.ForeignKey(get_user_model(), verbose_name="ユーザー2", on_delete=models.CASCADE, related_name="conversation_user2")
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta():
        verbose_name_plural = '06-01.DMルーム'
        db_table = 'conversation_room'
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_conversation')
        ]

    def __str__(self):
        return f'Conversation: {self.user1} - {self.user2}'


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, verbose_name="DMルーム", on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(get_user_model(), verbose_name="送信したユーザー", on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(verbose_name="メッセージ内容")
    is_read = models.BooleanField(verbose_name="既読", default=False)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta():
        verbose_name_plural = '06-02.DMメッセージ内容'
        db_table = 'dm_message'

    def __str__(self):
        return f'Message: {self.sender}'


class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, verbose_name="メッセージ", on_delete=models.CASCADE)
    file_url = models.FileField(verbose_name="ファイル保存先", upload_to=upload_dm_image_to)
    file_type = models.SmallIntegerField(verbose_name="ファイルタイプ")
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)


    class Meta():
        verbose_name_plural = '06-03.DMメッセージファイル'
        db_table = 'dm_message_attachment'

    def __str__(self):
        return f'MessageAttachment: {self.id}'


class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name="通知を受け取るユーザー", on_delete=models.CASCADE, related_name="notifications", db_index=True)
    sender = models.ForeignKey(get_user_model(), verbose_name="通知したユーザー", on_delete=models.SET_NULL, blank=True, null=True, related_name="notified", db_index=True)
    action_type = models.CharField(verbose_name="通知タイプ", choices=ACTION_TYPE, max_length=50, db_index=True)
    article = models.ForeignKey(Article, verbose_name="記事", on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    comment = models.ForeignKey(Comment, verbose_name="コメント", on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    like = models.ForeignKey(ArticleLike, verbose_name="いいね", on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    follow = models.ForeignKey(Follow, verbose_name="フォロー", on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    # dm = models.ForeignKey(Follow, verbose_name="DM", on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(verbose_name='既読', default=0, db_index=True, blank=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta():
        verbose_name_plural = '05-01.通知'
        db_table = 'notification'

    def __str__(self):
        return f'Notification: {self.user} - {self.action_type}'