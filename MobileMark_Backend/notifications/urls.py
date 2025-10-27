from django.urls import path
from .views import UserNotificationView,ProductNotifySubscribeView

urlpatterns = [
    path('admin/user-notifications/', UserNotificationView.as_view(), name='user-notifications'),
    path('admin/user-notifications/<int:pk>/', UserNotificationView.as_view(), name='user-notification-delete'),
    path("notifications/subscribe/<int:product_id>/", ProductNotifySubscribeView.as_view(), name="product-subscribe")
]