import os
import payjp

from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
# キャッシュ
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from common.myiste_def import *


class PayView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/demo/pay.html'
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
    template_name = 'mysite/demo/cache_test.html'

    def get(self, request, *args, **kwargs):
        name = request.GET.get('name', None)
        return render(request, self.template_name, {
            'answer': prime_factorize(9867280421310721),
            'time': timezone.now(),
            'name': name,
        })
