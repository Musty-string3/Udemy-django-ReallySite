from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('index/', views.ArticleIndexView.as_view(), name='index'),
    path('new/', views.ArticleNewView.as_view(), name='new'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ArticleEditView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='delete'),
    path('tags/<str:name>/', views.ArticleTagView.as_view(), name='tag_detail'),
    path('<int:pk>/like/', views.ArticleLikeView.as_view(), name='like_detail'),
]
