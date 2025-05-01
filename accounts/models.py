from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils import timezone
from django.core.validators import FileExtensionValidator

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_profile')
    email_token = models.CharField(max_length=200, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def generate_token(self):
        self.email_token = str(uuid.uuid4())
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.email_profile.save()
    if hasattr(instance, 'user_profile'):
        instance.user_profile.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    team = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    weekly_summary = models.BooleanField(default=True)
    profile_complete = models.FloatField(default=0)  # Percentage of profile completion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def calculate_profile_complete(self):
        """Calculate the percentage of profile completion"""
        fields = ['first_name', 'last_name', 'email', 'department', 'team', 'role', 'profile_photo']
        completed = sum(1 for field in fields if getattr(self, field))
        self.profile_complete = (completed / len(fields)) * 100
        self.save()

class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    device_info = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # Bootstrap icon class
    earned_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class UserCertificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='certificates/')
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
  