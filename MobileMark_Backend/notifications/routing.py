from django.urls import re_path

# Import consumer locally inside the list to avoid AppRegistryNotReady
def get_websocket_urlpatterns():
    from .consumers import NotificationConsumer
    return [
        re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
    ]

websocket_urlpatterns = get_websocket_urlpatterns()