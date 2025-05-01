from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TrainingModule, UserModuleProgress, LearningPath

class ModuleInline(admin.TabularInline):
    model = TrainingModule
    fields = ('title', 'order', 'difficulty', 'estimated_duration', 'is_active')
    ordering = ('order',)
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

@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'path_with_order', 'difficulty', 'estimated_duration', 
                   'is_active', 'prerequisite_count', 'updated_at')
    list_filter = ('difficulty', 'is_active', 'learning_path')
    search_fields = ('title', 'description')
    ordering = ('learning_path', 'order', 'title')
    list_editable = ('is_active',)
    filter_horizontal = ('prerequisites',)
    autocomplete_fields = ['learning_path']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'learning_path', 'order', 'is_active')
        }),
        ('Content', {
            'fields': ('content', 'estimated_duration', 'difficulty', 'icon_name')
        }),
        ('Completion', {
            'fields': ('completion_badge',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [ModulePrerequisiteInline]
    
    def path_with_order(self, obj):
        if obj.learning_path:
            path_url = reverse('admin:modules_learningpath_change', args=[obj.learning_path.id])
            return mark_safe(f'<a href="{path_url}">{obj.learning_path.name}</a> (#{obj.order})')
        return '-'
    path_with_order.short_description = 'Learning Path (Order)'
    path_with_order.admin_order_field = 'learning_path__name'

    def prerequisite_count(self, obj):
        count = obj.prerequisites.count()
        if count:
            return format_html(
                '{} module{}',
                count,
                's' if count != 1 else ''
            )
        return '-'
    prerequisite_count.short_description = 'Prerequisites'

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new module
            # Set the order to be the last in its learning path
            if obj.learning_path:
                obj.order = obj.get_next_order()
        super().save_model(request, obj, form, change)

@admin.register(UserModuleProgress)
class UserModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'completion_percentage', 'is_completed', 
                   'started_at', 'completed_at', 'time_spent')
    list_filter = ('is_completed', 'module__learning_path', 'module')
    search_fields = ('user__username', 'module__title')
    readonly_fields = ('started_at', 'last_accessed', 'completed_at', 'time_spent')
    raw_id_fields = ('user', 'module')
    fieldsets = (
        (None, {
            'fields': ('user', 'module', 'completion_percentage', 'is_completed')
        }),
        ('Timing', {
            'fields': ('started_at', 'last_accessed', 'completed_at', 'time_spent'),
            'classes': ('collapse',)
        })
    )
