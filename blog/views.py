from django.shortcuts import render
from django.core.paginator import Paginator

from .models import Article


def index(request):
    template_name = 'blog/blogs.html'
    page_number = request.GET.get('page')

    articles = Article.objects.all()
    # 1ページの記事の表示を変更
    paginator = Paginator(articles, 2).get_page(page_number)

    context = {
        'paginator_articles': paginator,
        'page_number': page_number,
    }
    return render(request, template_name, context)


def article(request, pk):
    template_name = 'blog/article.html'

    article = Article.objects.get(pk=pk)
    context = {
        'article': article,
    }
    return render(request, template_name, context)
