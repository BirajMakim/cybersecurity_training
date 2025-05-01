from django.urls import path
from . import views

app_name = 'modules'

urlpatterns = [
    path('', views.learning_path_list, name='learning_path_list'),  # Make this the default view
    path('path/<int:path_id>/', views.learning_path_detail, name='learning_path_detail'),
    path('list/', views.module_list, name='module_list'),
    path('start-new/', views.start_new_course, name='start_new_course'),
    path('start/<int:module_id>/', views.start_module, name='start_module'),
    path('detail/<int:module_id>/', views.module_detail, name='module_detail'),
    path('update-progress/<int:module_id>/', views.update_progress, name='update_progress'),
] 