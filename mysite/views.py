from django.shortcuts import render
from django.http import HttpResponse
from blog.models import Article

def index(request):
    last_three_articles = Article.objects.all()[:3]
    context = {
        'title': 'Really Site',
        'last_three_articles': last_three_articles,
    }
    print(context)
    return render(request, 'mysite/index.html', context)
