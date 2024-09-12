from django.urls import path

# キャッシュ
from django.views.decorators.cache import cache_page

from . import views

app_name = 'demo'
urlpatterns = [
    path('pay/', views.PayView.as_view(), name='pay'),
    path('cache_test/', cache_page(30)(views.CacheTestView.as_view()), name='cache'),
]