from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from mysite.models.profile_models import Profile


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        # ユーザーがemailを持ってなかったらエラーを吐かせる
        if not email:
            raise ValueError('User must have an email address（ユーザー登録にはemailが必須です。）')
        user = self.model(
            email = self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    # unique=Trueで一意のメールアドレスしか受け付けない
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


# ユーザー（User）が作成された直後（post_save）に以下の関数を処理する
# Udemyの64
@receiver(post_save, sender=User)
def create_onetoone(sender, **kwargs):
    if kwargs['created']:

        Profile.objects.create(user=kwargs['instance'])