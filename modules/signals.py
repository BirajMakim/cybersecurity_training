from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import UserModuleProgress, Notification

@receiver(post_save, sender=UserModuleProgress)
def handle_module_progress(sender, instance, created, **kwargs):
    if created:
        # User started a new module
        Notification.objects.create(
            user=instance.user,
            module=instance.module,
            message=f"You have started the module: {instance.module.title}"
        )
    elif instance.is_completed and instance.progress == 100:
        # User completed the module
        Notification.objects.create(
            user=instance.user,
            module=instance.module,
            message=f"Congratulations! You completed the module: {instance.module.title}"
        ) 