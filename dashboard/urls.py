from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('learning-path/', views.learning_path, name='learning_path'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
] 