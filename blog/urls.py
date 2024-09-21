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
    # 非同期いいね
    path('<int:pk>/like/', views.ArticleLikeView.as_view(), name='like_detail'),
    # 検索機能
    path('search/', views.SearchView.as_view(), name='search'),
    path('cart/', views.ArticleInCartView.as_view(), name='cart'),
    path('purchase/', views.ArticlePurchaseView.as_view(), name='purchase'),
    # フォロー
    path('follow/<int:pk>', views.FollowView.as_view(), name='follow'),
    # DM
    path('dm/index', views.DMIndexView.as_view(), name="dm_index"),
    path('dm/<int:pk>', views.DMDetailView.as_view(), name="dm_detail"),
]
