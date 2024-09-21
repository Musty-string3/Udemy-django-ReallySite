import os

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings


def upload_image_to(instance, filename):
    user_id = str(instance.user.id)
    return os.path.join('profile_images', user_id, filename)

PREFECTURE_CHOICE = (
    (0, '選択なし'),
    (1, '北海道'),
    (2, '青森'),
    (3, '岩手'),
    (4, '宮城'),
    (5, '秋田'),
    (6, '山形'),
    (7, '福島'),
    (8, '茨城'),
    (9, '栃木'),
    (10, '群馬'),
    (11, '埼玉'),
    (12, '千葉'),
    (13, '東京'),
    (14, '神奈川'),
    (15, '新潟'),
    (16, '富山'),
    (17, '石川'),
    (18, '福井'),
    (19, '山梨'),
    (20, '長野'),
    (21, '岐阜'),
    (22, '静岡'),
    (23, '愛知'),
    (24, '三重'),
    (25, '滋賀'),
    (26, '京都'),
    (27, '大阪'),
    (28, '兵庫'),
    (29, '奈良'),
    (30, '和歌山'),
    (31, '鳥取'),
    (32, '島根'),
    (33, '岡山'),
    (34, '広島'),
    (35, '山口'),
    (36, '徳島'),
    (37, '香川'),
    (38, '愛媛'),
    (39, '高知'),
    (40, '福岡'),
    (41, '佐賀'),
    (42, '長崎'),
    (43, '熊本'),
    (44, '大分'),
    (45, '宮崎'),
    (46, '鹿児島'),
    (47, '沖縄')
)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='ユーザー', unique=True, on_delete=models.CASCADE, primary_key=True)
    username = models.CharField(verbose_name='ユーザー名', default='匿名ユーザー', max_length=50)
    zipcode = models.CharField(verbose_name='郵便番号', max_length=8, blank=True, null=True)
    prefecture = models.SmallIntegerField(verbose_name='都道府県',choices=PREFECTURE_CHOICE, default=0)
    city = models.CharField(verbose_name='市区町村', max_length=100, blank=True, null=True)
    address = models.CharField(verbose_name='住所', max_length=200, blank=True, null=True)
    image = models.ImageField(verbose_name='プロフィール画像', upload_to=upload_image_to, default='images/default.png', blank=True)
    follows = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='フォローしているユーザー', related_name='followed_by')
    is_public = models.BooleanField(verbose_name='プロフィールを公開', default=1)

    class Meta:
        verbose_name_plural = 'プロフィール'
        db_table = 'profile'

    def __str__(self):
        return self.username