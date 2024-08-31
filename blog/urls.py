from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('index/', views.ArticleIndexView.as_view(), name='index'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
    path('tags/<str:name>/', views.ArticleTagView.as_view(), name='tag_detail'),
]
