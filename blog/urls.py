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
    # 非同期コメント
    path('comment/new/', views.CommentNewView.as_view(), name='comment_new'),
    path('comment/<int:pk>/edit/', views.CommentEditView.as_view(), name='comment_edit'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    # 検索機能
    path('search/', views.SearchView.as_view(), name='search'),
    # 購入関係
    path('cart/', views.ArticleInCartView.as_view(), name='cart'),
    path('purchase/', views.ArticlePurchaseView.as_view(), name='purchase'),
    # 通知
    path('notification/', views.NotificationView.as_view(), name="notification"),
    # フォロー
    path('follow/<int:pk>', views.FollowView.as_view(), name='follow'),
    # DM
    path('dm/index', views.DMIndexView.as_view(), name="dm_index"),
    path('dm/<int:pk>/create', views.DMCreateView.as_view(), name="dm_create"),
    path('dm/<int:pk>', views.DMDetailView.as_view(), name="dm_detail"),
    path('ws_pra/dm/<str:room_name>/', views.chat_room, name='demo_chat_room'),
]
