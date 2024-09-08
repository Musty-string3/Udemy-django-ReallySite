from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('index/', views.ArticleIndexView.as_view(), name='index'),
    path('new/', views.ArticleNewView.as_view(), name='new'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
    path('edit/<int:pk>/', views.ArticleEditView.as_view(), name='edit'),
    path('tags/<str:name>/', views.ArticleTagView.as_view(), name='tag_detail'),
    path('<int:pk>/like/', views.ArticleLikeView.as_view(), name='like_detail'),
]
