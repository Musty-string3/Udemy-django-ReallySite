from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views import View
from django.utils import timezone
from datetime import timedelta

from .models import Article, Comment
from .forms import CommentForm


class ArticleIndexView(View):
    template_name = 'blog/blogs.html'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page')

        articles = Article.objects.all()
        # 1ページの記事の表示を変更
        paginator = Paginator(articles, 2).get_page(page_number)

        return render(request, self.template_name, {
            'paginator_articles': paginator,
            'page_number': page_number,
        })


class ArticleDetailView(View):
    template_name = 'blog/article.html'
    def days_ago_comment(self, comment_date):
        delta = timezone.now() - comment_date
        days_ago = delta.days

        if delta < timedelta(minutes=1):
            return 'たった今'
        elif delta < timedelta(hours=1):
            return f'{delta.seconds // 60}分前'
        elif delta < timedelta(days=1):
            return f'{delta.hours // 24}時間前'
        else:
            return f'{delta.days}日前'

    def get(self, request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        comments = Comment.objects.filter(article=article)
        comments_with_time = [(comment, self.days_ago_comment(comment.created_at)) for comment in comments]
        # self.days_ago_comment()
        print(comments_with_time)

        return render(request, self.template_name, {
            'article': article,
            'comments_with_time': comments_with_time,
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

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()

        comments = Comment.objects.filter(article=article)
        comments_with_time = [(comment, self.days_ago_comment(comment.created_at)) for comment in comments]

        return render(request, self.template_name, {
            'article': article,
            'comment_form': comment_form,
            'comments_with_time': comments_with_time,
        })