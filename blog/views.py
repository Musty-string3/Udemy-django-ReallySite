import os
import json
import payjp

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views import View
from django.db.models import Count

from .models import *
from .forms import CommentForm, ArticleNewForm
from common.myiste_def import *

# 非同期処理
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse


class ArticleIndexView(CustomLoginRequiredMixin, View):
    template_name = 'blog/blogs.html'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page')

        articles = Article.objects.annotate(
            like_count=Count('article_like'),
            comment_count=Count('comments'),
        )
        # 1ページの記事の表示を変更
        paginator = Paginator(articles, 3).get_page(page_number)

        # 決済未完了のorderを取得
        orders = Order.objects.filter(user=request.user, order_status=0)

        # タプルの内容をflat=Trueでリスト形式に変更
        purchased_article_ids = orders.values_list('article_id', flat=True)

        return render(request, self.template_name, {
            'page_title': 'ブログ一覧画面',
            'paginator_articles': paginator,
            'page_number': page_number,
            'purchased_article_ids': purchased_article_ids,
        })


class ArticleNewView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/blog_new.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'title': '新規ブログ作成',
        })

    def post(self, request, *args, **kwargs):
        article_new_form = ArticleNewForm(request.POST)
        print('request.POST.get', request.POST.get)

        if article_new_form.is_valid():
            # forms.pyの中でタグの設定などの処理を行う
            form = article_new_form.save(request.user, commit=False)
            form.save()

            messages.success(request, '記事を作成しました。')
            return redirect('blog:detail', form.id)
        else:
            messages.error(request, f'記事の作成に失敗しました。\n{request.POST.get}')

        return render(request, self.template_name, {
            'article_new_form': article_new_form,
        })


class ArticleEditView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/blog_new.html'

    def get(self, request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        tag_list = article.tags.all()
        tag_string = '、'.join([tag.name for tag in tag_list])

        return render(request, self.template_name, {
            'title': 'ブログ編集',
            'article_title': article.title,
            'article_text': article.text,
            'tags': tag_string,
            'article_is_public': article.is_public,
            'article_sell_flag': article.sell_flag,
            'article_price': article.price,
        })

    def post(self, request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        article_new_form = ArticleNewForm(request.POST, instance=article)
        print('request.POST.get', request.POST.get)

        if article_new_form.is_valid():
            # forms.pyの中でタグの設定などの処理を行う
            form = article_new_form.save(request.user, commit=False)
            form.save()

            messages.success(request, '記事を作成しました。')
            return redirect('blog:detail', form.id)
        else:
            article_new_form = ArticleNewForm(instance=article)
            tags = request.POST.get('tags')
            messages.error(request, '記事の作成に失敗しました。')

        return render(request, self.template_name, {
            'article_new_form': article_new_form,
            'article_title': article_new_form['title'].initial,
            'article_text': article_new_form['text'].initial,
            'tags': tags,
            'article_is_public': article_new_form['is_public'].initial,
            'article_sell_flag': article_new_form['sell_flag'].initial,
            'article_price': article_new_form['price'].initial,
        })


class ArticleDetailView(CustomLoginRequiredMixin, View):
    template_name = 'blog/article.html'

    def get(self, request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        print(article.tags.all())

        comments = Comment.objects.filter(article=article)
        comments_with_time = [(comment, days_ago_comment(comment.created_at)) for comment in comments]
        like_count = ArticleLike.objects.filter(article=article).count()

        return render(request, self.template_name, {
            'article': article,
            'comments_with_time': comments_with_time,
            'like_count': like_count,
        })

    def post(self, request, pk, *args, **kwargs):
        # textareaのnameがrequest.POST.get('comment')に送られてくる
        request_comment = request.POST.get('comment')

        try:
            article = Article.objects.get(pk=pk)
        except Comment.DoesNotExist:
            messages.error(request, 'コメントの投稿に失敗しました。')
            return redirect('blog:index')

        comment_form = CommentForm(request.POST)

        # 非同期処理を使わない、いいね機能
        # if request.POST.get('like_count', None):
        #     if request.POST.get('like_delete', None):
        #         ArticleLike.objects.filter(user=request.user, article=article).delete()
        #     elif article_like_exists(article, request.user):
        #         ArticleLike.objects.create(user=request.user, article=article)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
        else:
            messages.error(request, '処理に失敗しました。')
            return redirect('blog:detail', pk)

        comments = Comment.objects.filter(article=article)
        comments_with_time = [(comment, days_ago_comment(comment.created_at)) for comment in comments]
        like_count = ArticleLike.objects.filter(article=article).count()

        return render(request, self.template_name, {
            'article': article,
            'comment_form': comment_form,
            'comments_with_time': comments_with_time,
            'like_count': like_count,
        })


class ArticleDeleteView(CustomLoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        try:
            Article.objects.get(pk=pk).delete()
            messages.success(request, '記事を削除しました。')
        except Article.DoesNotExist:
            messages.error(request, '記事の削除に失敗しました。')
        return redirect('blog:index')

class ArticleTagView(CustomLoginRequiredMixin, View):
    template_name = 'blog/blogs.html'

    def get(self, request, name, *args, **kwargs):
        page_number = request.GET.get('page')
        tag = ArticleTag.objects.get(name=name)
        tag_obj = tag.articles.all()
        print(tag_obj)

        paginator = Paginator(tag_obj, 3).get_page(page_number)

        return render(request, self.template_name, {
            'page_title': '記事一覧 #{}'.format(name),
            'paginator_articles': paginator,
            'page_number': page_number,
        })

class ArticleLikeView(CustomLoginRequiredMixin, View):

    def get(self, request, pk, *args, **kwargs):
        context = {
            "message": "error",
        }
        return JsonResponse(context)

    def post(self, request, pk, *args, **kwargs):
        # javascriptから送られてきたbodyの中身を取得
        data = json.loads(request.body)
        # bodyの中のarticle_pkを取得
        article_pk = data.get('article_pk')

        context = {
            "message": "error",
        }
        try:
            article = Article.objects.get(pk=article_pk)
            # article = Article.objects.get(pk=pk)でも可能
        except Article.DoesNotExist:
            messages.error(request, '存在しない記事です。')
            return redirect('blog:index')

        try:
            like_exists = article_like_exists(article, request.user)

            if like_exists:
                ArticleLike.objects.create(user=request.user, article=article)
                context["method"] = "create"
            else:
                ArticleLike.objects.filter(user=request.user, article=article).delete()
                context["method"] = "delete"
            context['message'] = 'success'
            # いいねのカウント数を集計
            context["like_count"] = article.article_like.count()
        except:
            pass

        return JsonResponse(context)


class ArticleInCartView(CustomLoginRequiredMixin, View):
    # カートに入れるを選択するとorderが作成され、カートから外すを選択でorderを削除する処理

    def get(self, request, *args, **kwargs):
        article_id = request.GET.get('article_id')
        delete = request.GET.get('delete', None)

        if delete:
            try:
                orders = Order.objects.filter(user=request.user, article=article_id, charge_type=0)
                orders.delete()
            except Order.DoesNotExist as e:
                messages.error(request, f'商品をカートから外す処理に失敗しました。{e}')
            return redirect('blog:index')
        else:
            try:
                article = Article.objects.get(pk=article_id)
            except Article.DoesNotExist:
                messages.error(request, '記事の取得に失敗しました。')
                return redirect('blog:index')

            order = Order.objects.create(
                user=request.user,
                article=article,
                price=article.price,
                charge_type=0,
                order_status=0,
            )
            return redirect('blog:index')

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


class ArticlePurchaseView(CustomLoginRequiredMixin, View):
    # Orderの決済未登録を取得して表示させる
    # 購入できたらUserItemにデータを作成する

    template_name = 'mysite/article_purchase.html'
    payjp.api_key = os.environ['PAYJP_SECRET_KEY']
    public_key = os.environ['PAYJP_PUBLIC_KEY']

    def get(self, request, *args, **kwargs):
        article_id = request.GET.get('article_id')
        print(article_id)
        try:
            aritcle = Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            messages.error(request, '記事の取得に失敗しました。')
        return render(request, self.template_name, {
            'amount': self.amount,
            'public_key': self.public_key,
        })

    # 購入した直後の処理
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