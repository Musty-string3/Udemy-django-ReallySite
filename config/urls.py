from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from mysite import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='top'),
    path('blog/', include('blog.urls')),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
]
