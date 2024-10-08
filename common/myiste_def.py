from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


from blog.models import ArticleLike, UserItem

class CustomLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'ログインが必要です。')
            redirect('login')
        return super().dispatch(request, *args, **kwargs)


def days_ago_comment(comment_date):
    delta = timezone.now() - comment_date
    days_ago = delta.days

    if delta < timedelta(minutes=1):
        return 'たった今'
    elif delta < timedelta(hours=1):
        return f'{delta.seconds // 60}分前'
    elif delta < timedelta(days=1):
        return f'{delta.seconds // 3600}時間前'
    else:
        return f'{delta.days}日前'

def article_like_exists(article, user):
    if ArticleLike.objects.filter(user=user, article=article).exists():
        return False
    else:
        return True

def prime_factorize(num):
    a = []
    while num % 2 == 0:
        a.append(2)
        num //= 2
    f = 3
    while f * f <= num:
        if num % f == 0:
            a.append(f)
            num //= f
        else:
            f += 2
    if num != 1:
        a.append(num)
    return a

def user_item_index(request, user, charge_type):
    user_item = UserItem.objects.filter(user=user, charge_type=charge_type)
    return user_item
