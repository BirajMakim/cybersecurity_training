from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('learning-path/', views.learning_path, name='learning_path'),
    path('profile/', views.profile_redirect, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/get-unread-count/', views.get_unread_count, name='get_unread_count'),
    path('notifications/get-latest/', views.get_latest_notifications, name='get_latest_notifications'),
    path('settings/', views.settings, name='settings'),
] 