# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.user = self.scope.get("user")
        if self.user.is_anonymous:
            await self.close()
            return

        # Personal group for user
        self.personal_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.personal_group, self.channel_name)

        # Optional broadcast group
        await self.channel_layer.group_add("broadcast", self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "personal_group"):
            await self.channel_layer.group_discard(self.personal_group, self.channel_name)
        await self.channel_layer.group_discard("broadcast", self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
            return

        title = data.get("title", "")
        message = data.get("message", "")
        image_url = data.get("imageUrl")
        target_user_id = data.get("userId")  # optional

        # Save to database safely
        notification = await database_sync_to_async(Notification.objects.create, thread_sensitive=True)(
            title=title,
            message=message,
            image_url=image_url,
            user_id=target_user_id if target_user_id else None,
        )

        notification_data = {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "imageUrl": notification.image_url,
            "createdAt": notification.created_at.isoformat(),
            "userId": notification.user_id,
        }

        # Determine which group to send
        group_name = f"user_{target_user_id}" if target_user_id else "broadcast"

        await self.channel_layer.group_send(
            group_name,
            {"type": "send_notification", "message": notification_data},
        )

    async def send_notification(self, event):
        """Send notification to WebSocket client"""
        await self.send(text_data=json.dumps(event["message"]))