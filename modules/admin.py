from django.contrib import admin
from .models import TrainingModule, UserModuleProgress

@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'estimated_duration', 'order', 'is_active')
    list_filter = ('difficulty', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('order', 'title')
    list_editable = ('order', 'is_active')

@admin.register(UserModuleProgress)
class UserModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'completion_percentage', 'is_completed', 'started_at', 'last_accessed')
    list_filter = ('is_completed', 'module')
    search_fields = ('user__username', 'module__title')
    readonly_fields = ('started_at', 'last_accessed', 'completed_at')
    raw_id_fields = ('user',)
