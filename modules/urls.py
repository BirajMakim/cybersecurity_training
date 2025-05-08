from django.urls import path
from . import views

app_name = 'modules'

urlpatterns = [
    path('', views.module_list, name='module_list'),
    path('start/<slug:slug>/', views.start_module, name='start_module'),
    path('resume/<slug:slug>/', views.resume_module, name='resume_module'),
    path('progress/<slug:slug>/', views.update_progress, name='update_progress'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/mark-read/', 
         views.mark_notification_read, name='mark_notification_read'),
    path('start-new/', views.start_new_course, name='start_new_course'),
    path('learning-paths/', views.learning_path_list, name='learning_path_list'),
    path('learning-paths/<int:path_id>/', views.learning_path_detail, name='learning_path_detail'),
    path('<slug:slug>/quiz/', views.module_quiz, name='module_quiz'),
    path('<slug:slug>/', views.module_detail, name='module_detail'),
] 