from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('index/', views.ArticleIndexView.as_view(), name='index'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
]
