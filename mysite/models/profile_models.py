import os

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings


def upload_image_to(instance, filename):
    user_id = str(instance.user.id)
    return os.path.join('images', user_id, filename)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='ユーザー', unique=True, on_delete=models.CASCADE, primary_key=True)
    username = models.CharField(verbose_name='ユーザー名', default='匿名ユーザー', max_length=50)
    zipcode = models.CharField(verbose_name='郵便番号', default='', max_length=8)
    prefecture = models.CharField(verbose_name='都道府県',default='', max_length=8)
    city = models.CharField(verbose_name='市区町村', default='', max_length=100)
    address = models.CharField(verbose_name='住所', default='', max_length=200)
    image = models.ImageField(verbose_name='プロフィール画像', upload_to=upload_image_to, default='images/default.png')

    class Meta:
        verbose_name_plural = 'プロフィール'
        db_table = 'profile'

    def __str__(self):
        return self.username