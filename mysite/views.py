import os
import payjp

from django.utils import timezone
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.db.models import Count
# キャッシュ
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from blog.models import Article, ArticleLike
from mysite.forms import UserCreateForm, ProfileForm
from common.myiste_def import CustomLoginRequiredMixin, prime_factorize


class TopView(View):
    template_name = 'mysite/index.html'
    def get(self, request, *args, **kwargs):
        last_three_articles = Article.objects.all().order_by('-created_at')[:3]
        popular_articles = Article.objects.annotate(
            like_count=Count('article_like'),
            comment_count=Count('comments')).order_by('-like_count')[:2]

        return render(request, self.template_name, {
            'title': 'Really Site',
            'last_three_articles': last_three_articles,
            'popular_articles': popular_articles,
        })


class Login(LoginView):
    template_name = 'mysite/auth.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, f'すでに{request.user}でログインしています。')
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'ログインしました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ユーザー名またはパスワードが間違っています。')
        return super().form_invalid(form)


class Signup(View):
    template_name = 'mysite/auth.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, f'すでに{request.user}でログインしています。')
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        signup_btn = 'サインイン'
        return render(request, self.template_name, {
            'signup_btn': signup_btn,
        })

    def post(self, request, *args, **kwargs):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.is_active = False
            user.save()
            # ログインさせる
            login(request, user)
            messages.success(request, 'ユーザー登録が完了しました。')
            return redirect('/')
        else:
            messages.error(request, 'ユーザー登録に失敗しました。（既に同じメールアドレスを持ったユーザーが存在します。）')
            return redirect('signup')


class MypageView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/mypage.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
        })

    def post(self, request, *args, **kwargs):
        print(request.FILES)
        print(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'プロフィール情報が更新されました。')
        else:
            messages.error(request, 'プロフィール情報が更新できませんでした。')
            return redirect('mypage')

        return render(request, self.template_name, {
        })


class ContactView(View):
    template_name = 'mysite/contact.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name, {
        })

    def post(self, request, *args, **kwargs):
        print(request.POST.get)
        # ------ email送信
        subject = 'お問い合わせがありました。'
        message = "お問い合わせがありました。\n\n名前: {}\nメールアドレス: {}\n内容: {}\n".format(
            request.POST.get('name'),
            request.POST.get('email'),
            request.POST.get('contact'),
        )
        email_from = os.environ['EMAIL_HOST_USER']
        email_to = [os.environ['EMAIL_HOST_USER'], ]
        try:
            send_mail(subject, message, email_from, email_to)
            messages.success(request, 'お問い合わせメールの送信をしました。')
        except Exception as e:
            messages.error(request, f'メールの送信に失敗しました。エラーコード{e}')
            return redirect('/')
        return render(request, self.template_name, {
        })


class PayView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/pay.html'
    payjp.api_key = os.environ['PAYJP_SECRET_KEY']
    public_key = os.environ['PAYJP_PUBLIC_KEY']
    amount = 1000

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'amount': self.amount,
            'public_key': self.public_key,
        })

    def post(self, request, *args, **kwargs):
        print(request.POST.get)
        # 作成されたトークンをもとに作成されたのは誰かを判定して作成する
        customer = payjp.Customer.create(
            email = 'example@pay.jp',
            card = request.POST.get('payjp-token'),
        )
        # 支払いを行う
        charge = payjp.Charge.create(
            amount = self.amount,
            currency = 'jpy', #通貨のこと
            customer = customer.id,
            description = '決済テスト',
        )
        return render(request, self.template_name, {
            'amount': self.amount,
            'public_key': self.public_key,
            'charge': charge,
            'card': request.POST.get('payjp-token'),
        })

# @method_decorator(cache_page(30), name='dispatch')
# @method_decoratorを使って、cache_pageデコレータをdispatchメソッドに適用
class CacheTestView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/cache_test.html'

    def get(self, request, *args, **kwargs):
        name = request.GET.get('name', None)
        return render(request, self.template_name, {
            'answer': prime_factorize(9867280421310721),
            'time': timezone.now(),
            'name': name,
        })