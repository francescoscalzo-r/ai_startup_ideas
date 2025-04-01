from django.urls import path
from . import views
from .like_views import like_idea

app_name = 'ideas'

urlpatterns = [
    path('', views.home, name='home'),
    path('idee/', views.idea_list, name='idea_list'),
    path('idee/<int:pk>/', views.idea_detail, name='idea_detail'),
    path('idee/nuova/', views.idea_create, name='idea_create'),
    path('idee/<int:pk>/like/', like_idea, name='idea_like'),
    path('quadranti/', views.quadrante_list, name='quadrante_list'),
    path('quadranti/<int:pk>/', views.quadrante_detail, name='quadrante_detail'),
    path('esporta/', views.export_ideas, name='export_ideas'),
    path('profilo/', views.user_profile, name='user_profile'),
]
