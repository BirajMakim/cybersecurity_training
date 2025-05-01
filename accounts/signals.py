from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from dashboard.utils import create_user_notification

@receiver(pre_save, sender=UserProfile)
def store_old_profile_data(sender, instance, **kwargs):
    """Store old profile data for comparison after save"""
    try:
        instance._old_instance = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        instance._old_instance = None

@receiver(post_save, sender=UserProfile)
def notify_profile_changes(sender, instance, created, **kwargs):
    """Create notifications for profile changes not caught in views"""
    if created:
        create_user_notification(
            instance.user,
            "Welcome! Your profile has been created.",
            'success'
        )
        return

    old_instance = getattr(instance, '_old_instance', None)
    if not old_instance:
        return

    # Check for changes in other fields that might not be covered in views
    if old_instance.role != instance.role:
        create_user_notification(
            instance.user,
            f"Your role has been updated to {instance.role}",
            'info'
        )

    if old_instance.team != instance.team:
        create_user_notification(
            instance.user,
            f"Your team has been updated to {instance.team}",
            'info'
        )

    # Add more field comparisons as needed 