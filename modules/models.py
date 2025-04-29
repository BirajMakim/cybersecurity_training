from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class TrainingModule(models.Model):
    DIFFICULTY_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    estimated_duration = models.IntegerField(help_text="Duration in minutes")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='basic')
    icon_name = models.CharField(max_length=50, help_text="Bootstrap icon name (e.g., 'shield-lock')", default='book')
    order = models.IntegerField(default=0, help_text="Order in which the module appears")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

class UserModuleProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'module']
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({self.completion_percentage}%)"
