from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
# キャッシュ
from django.views.decorators.cache import cache_page

from mysite import views
from config import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
    path('demo/', include('demo.urls')),
    path('', views.TopView.as_view(), name='top'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('mypage/', views.MypageView.as_view(), name='mypage'),
    path('author/<int:pk>', views.AuthorView.as_view(), name='author'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]
urlpatterns += static(settings.MEDIA_URL,
                document_root=settings.MEDIA_ROOT)