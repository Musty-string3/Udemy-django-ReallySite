from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views import View
from django.contrib import messages

from blog.models import Article
from mysite.forms import UserCreateForm

def index(request):
    last_three_articles = Article.objects.all()[:3]
    context = {
        'title': 'Really Site',
        'last_three_articles': last_three_articles,
    }
    print(context)
    return render(request, 'mysite/index.html', context)


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
            messages.success(request, 'ユーザー登録が完了しました。')
            return redirect('/')