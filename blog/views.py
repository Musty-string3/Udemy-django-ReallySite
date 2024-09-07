import json

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views import View
from django.db.models import Count

from .models import Article, Comment, ArticleLike, ArticleTag
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

        return render(request, self.template_name, {
            'page_title': 'ブログ一覧画面',
            'paginator_articles': paginator,
            'page_number': page_number,
        })


class ArticleNewView(CustomLoginRequiredMixin, View):
    template_name = 'mysite/new.html'

    def get(self, request, *args, **kwargs):
        article_new_form = ArticleNewForm()
        

        return render(request, self.template_name, {
            
        })

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            
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
            return redirect('blog:detail', pk=pk)

        comments = Comment.objects.filter(article=article)
        comments_with_time = [(comment, days_ago_comment(comment.created_at)) for comment in comments]
        like_count = ArticleLike.objects.filter(article=article).count()

        return render(request, self.template_name, {
            'article': article,
            'comment_form': comment_form,
            'comments_with_time': comments_with_time,
            'like_count': like_count,
        })


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