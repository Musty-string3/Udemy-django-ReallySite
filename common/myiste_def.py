import redis
import json
import pprint

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail

from datetime import datetime, timezone, timedelta


from blog.models import *

class CustomLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'ログインが必要です。')
            redirect('login')
        return super().dispatch(request, *args, **kwargs)


def days_ago_comment(date):
    delta = timezone.now() - date
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


def notification_create(sender, receive_user=False, action_type=False, object=False, article=False):
    # ! receive_user = 通知を受け取るユーザー

    if action_type == "like":
        Notification.objects.get_or_create(
            user = receive_user,
            sender = sender,
            action_type = action_type,
            like = object,
        )
    elif action_type == "new_registration":
        Notification.objects.get_or_create(
            user = sender,
            action_type = action_type,
        )
    elif action_type == "comment":
        for re_user in receive_user:
            if sender != re_user.user:
                print("送信する相手", re_user.user)
                Notification.objects.create(
                    user = receive_user,
                    sender = re_user.user,
                    action_type = action_type,
                    comment = object,
                )
        # 投稿主にコメントが来た通知を送る
        Notification.objects.create(
            user = article.author,
            sender = sender,
            action_type = action_type,
            comment = object,
        )
    elif action_type == "follow":
        Notification.objects.get_or_create(
            user = receive_user,
            sender = sender,
            action_type = action_type,
            follow = object,
        )
    elif action_type == "purchase":
        Notification.objects.create(
            user = sender,
            action_type = action_type,
            article=article
        )
    elif action_type == "dm":
        notification_exists = Notification.objects.filter(
                user=receive_user, sender=sender, action_type="dm", is_read=False
            ).exists()

        # メッセージの既読をしていなかったら通知する
        if not notification_exists:
            Notification.objects.create(
                user = receive_user,
                sender = sender,
                action_type = action_type,
                dm = object,
            )

    return True



def filter_notifications(user, action_type, context):

    if action_type == "all":
        context['title'] = '通知一覧'
        context['notifications'] = Notification.objects.filter(user=user).order_by('-created_at')

    elif action_type == "comment":
        context['title'] = '通知一覧（コメント）'
        context['notifications'] = Notification.objects.filter(user=user, action_type="comment").order_by('-created_at')

    elif action_type == "like":
        context['title'] = '通知一覧（いいね）'
        context['notifications'] = Notification.objects.filter(user=user, action_type="like").order_by('-created_at')

    elif action_type == "follow":
        context['title'] = '通知一覧（フォロー）'
        context['notifications'] = Notification.objects.filter(user=user, action_type="follow").order_by('-created_at')

    elif action_type == "purchase":
        context['title'] = '通知一覧（購入）'
        context['notifications'] = Notification.objects.filter(user=user, action_type="purchase").order_by('-created_at')

    elif action_type == "dm":
        context['title'] = '通知一覧（DM）'
        context['notifications'] = Notification.objects.filter(user=user, action_type="dm").order_by('-created_at')
    else:
        context['notifications'] = Notification.objects.filter(user=user).order_by('-created_at')

    return context



def create_email(subject, name, email, contact=False, articles=False, price=False):
    email_from = os.environ['EMAIL_HOST_USER']
    email_to = [os.environ['EMAIL_HOST_USER'], ]

    # ------ お問い合わせのemail送信
    if subject == "お問い合わせがありました。":
        message = "お問い合わせがありました。\n\n名前: {}\nメールアドレス: {}\n内容: {}\n".format(
            name,
            email,
            contact,
        )

    # ------ お問い合わせのemail送信
    elif subject == "【購入メール】商品の購入をありがとうございます。":
        article_counts = len(articles)
        content = "この度は商品をご購入いただきありがとうございます。\n購入商品は{}点になります。\n引き続きサービスをよろしくぴょんだにゃん。".format(
            article_counts
        )
        sub_title = "名前: {}\nメールアドレス: {}\nお支払い金額:￥{}円\n".format(
            name,
            email,
            price,
        )
        article_detail = []
        for article in articles:
            article_detail.append("\n---------------\n購入商品: {}\n購入金額:￥{}円".format(
                article.title,
                article.price,
            ))
        message = "{}\n\n{}{}".format(
            content,
            sub_title,
            "".join(article_detail),
        )

    try:
        send_mail(subject, message, email_from, email_to)
        return "送信完了"
    except Exception as e:
        return f'メールの送信に失敗しました。エラーコード{e}'


## JSの文字列を一旦datetimeに変換して日本時間にした後にフォーマットをyyyy年mm月dd日hh-mmに変換する
def time_at_str(time_at):
    # 文字列を datetime に変換
    created_at_dt = datetime.fromisoformat(time_at).replace(tzinfo=timezone.utc)

    # JST (日本時間) に変換
    jst_time = created_at_dt.astimezone(timezone(timedelta(hours=9)))

    # フォーマット
    formatted_date = jst_time.strftime("%Y年%-m月%-d日%H:%M")

    return formatted_date

## キャッシュをredisに保存する
def article_set_item(articles, purchased_article_ids, user_item_ids):
    """ 記事をjsonに変換する """

    print("redisでのキャッシュを保存する\n")
    item = {}

    item["articles"] = []
    for article in articles:
        article_dict = {
            "id":               article.id,
            "title":            article.title,
            "text":             article.text,
            "image": [
                {
                    "id": img["id"],
                    "url": "/media/" + img["image"],
                }
                for img in article.image.values("id", "image")
            ],
            "created_at":       time_at_str(article.created_at.isoformat()),  ## JSONでシリアライズしないとエラーになってしまうため、isoformatを使用
            "updated_at":       time_at_str(article.updated_at.isoformat()),
            "like_count":       article.like_count,
            "comment_count":    article.comment_count,
            "view_total_count": article.view_total_count,
            "sell_flag":        article.sell_flag,
            "price":            article.price,
            "is_public":        article.is_public,
            "author": {
                "id":       getattr(article.author, "id"),
                "username": getattr(article.author.profile, "username"),
                "profile_image":    getattr(article.author.profile.image, "url"),
            },
        }
        item["articles"].append(article_dict)

    item["purchased_article_ids"] = list(purchased_article_ids)
    item["user_item_ids"] = list(user_item_ids)

    return item


## redisにキャッシュが保存されていれば取得する
def get_json_cache(redis_client, key):
    ## JSONを取得し、辞書に戻す
    try:
        retrieved_data = redis_client.get(key)
        if retrieved_data and redis_client.ping():
            return json.loads(retrieved_data)
        else:
            print("キャッシュ不使用")
    except TypeError:
        print("redisの有効期限切れ")
    except Exception as e:
        print(f"不明なエラー。エラー内容：{e}")

    return False