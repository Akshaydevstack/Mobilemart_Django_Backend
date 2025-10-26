from django.urls import path
from .views import UserNotificationView

urlpatterns = [
    # List & Create notifications
    path('admin/user-notifications/', UserNotificationView.as_view(), name='user-notifications'),

    # Delete a notification by ID
    path('admin/user-notifications/<int:pk>/', UserNotificationView.as_view(), name='user-notification-delete'),
]