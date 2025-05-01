from .models import Notification

def create_user_notification(user, message, notification_type='info'):
    """
    Create a notification for a user action.
    
    Args:
        user: The User instance
        message: Notification message
        notification_type: Type of notification (info, success, warning, error)
    """
    return Notification.objects.create(
        user=user,
        message=message,
        type=notification_type,
        is_read=False
    ) 