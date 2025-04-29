from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from . import views

class DashboardAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(login_required(views.dashboard)), name='dashboard'),
            path('profile/', self.admin_view(login_required(views.profile)), name='profile'),
            path('learning-path/', self.admin_view(login_required(views.learning_path)), name='learning_path'),
            path('notifications/', self.admin_view(login_required(views.notifications)), name='notifications'),
            path('settings/', self.admin_view(login_required(views.settings)), name='settings'),
        ]
        return custom_urls + urls

# Create an instance of the custom admin site
dashboard_admin_site = DashboardAdminSite(name='dashboard_admin')

# Register your models here if needed
# dashboard_admin_site.register(YourModel) 