from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TrainingModule, UserModuleProgress, LearningPath, Notification, ModuleContent, AssessmentQuestion, UserAssessment

class ModuleInline(admin.TabularInline):
    model = TrainingModule
    fields = ('title', 'difficulty', 'duration', 'is_active')
    extra = 0
    show_change_link = True

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_count', 'is_active', 'auto_unlock', 'created_at')
    list_filter = ('is_active', 'auto_unlock')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    list_editable = ('is_active', 'auto_unlock')
    inlines = [ModuleInline]
    
    def module_count(self, obj):
        count = obj.modules.count()
        active_count = obj.modules.filter(is_active=True).count()
        return format_html(
            '{} total ({} active)',
            count,
            active_count
        )
    module_count.short_description = 'Modules'

    def save_related(self, request, form, formsets, change):
        """Ensure modules are properly ordered after inline saves"""
        super().save_related(request, form, formsets, change)
        if change:  # Only reorder for existing paths
            form.instance.reorder_modules()

class ModulePrerequisiteInline(admin.TabularInline):
    model = TrainingModule.prerequisites.through
    fk_name = 'from_trainingmodule'
    extra = 1
    verbose_name = 'Prerequisite'
    verbose_name_plural = 'Prerequisites'

class ModuleContentInline(admin.TabularInline):
    model = ModuleContent
    extra = 1

class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 1

@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'duration', 'created_at')
    list_filter = ('difficulty', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ModuleContentInline, AssessmentQuestionInline]

@admin.register(UserModuleProgress)
class UserModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'progress', 'is_completed', 'last_accessed')
    list_filter = ('is_completed', 'module__difficulty')
    search_fields = ('user__username', 'module__title')
    readonly_fields = ('started_at', 'last_accessed', 'completed_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message', 'module__title')
    readonly_fields = ('created_at',)

@admin.register(ModuleContent)
class ModuleContentAdmin(admin.ModelAdmin):
    list_display = ('module', 'order', 'youtube_url')
    search_fields = ('module__title', 'text')
    ordering = ('module', 'order')

@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('module', 'question', 'correct_option')
    search_fields = ('module__title', 'question')
    ordering = ('module',)

@admin.register(UserAssessment)
class UserAssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'score', 'passed', 'submitted_at')
    search_fields = ('user__username', 'module__title')
    ordering = ('-submitted_at',)
