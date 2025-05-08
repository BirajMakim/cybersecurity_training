import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Notification, UserActivity
from modules.models import UserModuleProgress

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.user_id = self.scope["user"].id
            self.room_group_name = f"user_{self.user_id}"
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle any incoming messages if needed
        pass

    async def dashboard_update(self, event):
        """
        Send dashboard update to WebSocket
        """
        data = event["data"]
        
        # Get latest data
        dashboard_data = await self.get_dashboard_data()
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "dashboard_update",
            "data": dashboard_data
        }))

    @database_sync_to_async
    def get_dashboard_data(self):
        """
        Get latest dashboard data from database
        """
        # Get user's active modules
        active_modules = UserModuleProgress.objects.filter(
            user_id=self.user_id,
            is_completed=False
        ).select_related('module')
        
        # Get recent activities
        recent_activities = UserActivity.objects.filter(
            user_id=self.user_id
        ).order_by('-timestamp')[:5]
        
        # Get unread notifications
        unread_notifications = Notification.objects.filter(
            user_id=self.user_id,
            is_read=False
        ).count()
        
        return {
            "active_modules": [
                {
                    "id": progress.module.id,
                    "title": progress.module.title,
                    "progress": progress.progress
                }
                for progress in active_modules
            ],
            "recent_activities": [
                {
                    "id": activity.id,
                    "action": activity.action,
                    "timestamp": activity.timestamp.isoformat()
                }
                for activity in recent_activities
            ],
            "unread_notifications": unread_notifications
        } 