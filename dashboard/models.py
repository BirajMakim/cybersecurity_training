from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    link = models.URLField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='bi-info-circle')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'is_read', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"

    def get_icon_class(self):
        icon_map = {
            'info': 'bi-info-circle',
            'success': 'bi-check-circle',
            'warning': 'bi-exclamation-triangle',
            'error': 'bi-x-circle',
            'system': 'bi-gear',
        }
        return icon_map.get(self.type, 'bi-info-circle')

    def get_alert_class(self):
        alert_map = {
            'info': 'alert-info',
            'success': 'alert-success',
            'warning': 'alert-warning',
            'error': 'alert-danger',
            'system': 'alert-primary',
        }
        return alert_map.get(self.type, 'alert-info') 