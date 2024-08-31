from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Count

from blog.models import Article, ArticleLike
from mysite.forms import UserCreateForm, ProfileForm
from common.myiste_def import CustomLoginRequiredMixin


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
        profile_form = ProfileForm(request.POST)
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