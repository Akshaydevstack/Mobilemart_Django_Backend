# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Lazy import inside method
        from .models import Notification

        # Join a group for broadcast notifications
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def receive(self, text_data):
        """Receive notification from admin frontend"""
        from .models import Notification  # Lazy import here as well

        data = json.loads(text_data)
        title = data.get("title", "")
        message = data.get("message", "")
        image_url = data.get("imageUrl", "")
        user_id = data.get("userId")  # Optional, for user-specific notification

        # Save to DB
        notification = await database_sync_to_async(Notification.objects.create)(
            title=title,
            message=message,
            image_url=image_url,
            user_id=user_id if user_id else None
        )

        notification_data = {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "imageUrl": notification.image_url,
            "createdAt": str(notification.created_at),
            "userId": notification.user_id
        }

        # Broadcast to all users if user is None, else send to specific user group
        group_name = f"user_{user_id}" if user_id else "notifications"
        await self.channel_layer.group_send(
            group_name,
            {"type": "send_notification", "message": notification_data}
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["message"]))