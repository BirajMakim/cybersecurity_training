from .models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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

def send_dashboard_update(user_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "dashboard_update",
            "data": data,
        }
    ) 