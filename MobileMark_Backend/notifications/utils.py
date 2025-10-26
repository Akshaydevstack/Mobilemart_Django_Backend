from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast_notification(notification_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "send_notification",
            "message": notification_data
        }
    )