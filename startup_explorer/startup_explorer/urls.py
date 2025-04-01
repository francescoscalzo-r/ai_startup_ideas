from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from ideas import views as ideas_views
from ideas.auth_views import register_view, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ideas.urls')),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
]
