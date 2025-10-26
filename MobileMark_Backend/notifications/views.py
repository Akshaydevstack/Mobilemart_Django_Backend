from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Notification
from .serializers import NotificationSerializer

class UserNotificationView(APIView):
    permission_classes = [permissions.AllowAny]  # Open for testing

    def get(self, request):
        """
        List all notifications (latest first)
        """
        notifications = Notification.objects.all().order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete a notification by ID
        """
        if pk is None:
            return Response({"detail": "Notification ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            notification = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

        notification.delete()
        return Response({"detail": "Notification deleted"}, status=status.HTTP_204_NO_CONTENT)