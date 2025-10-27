from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Notification, ProductNotificationSubscription
from .serializers import NotificationSerializer
from products.models import Product
from django.db.models import Q




class UserNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            Q(user=request.user) | Q(user__isnull=True)
        ).order_by('-created_at')

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    def delete(self, request, pk=None):

        if pk is None:
            return Response({"detail": "Notification ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            notification = Notification.objects.get(
                pk=pk
            )
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found or not yours"}, status=status.HTTP_404_NOT_FOUND)

        notification.delete()
        return Response({"detail": "Notification deleted"}, status=status.HTTP_204_NO_CONTENT)







class ProductNotifySubscribeView(APIView):
    """
    Allows a logged-in user to subscribe to a product for availability notifications.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            obj, created = ProductNotificationSubscription.objects.get_or_create(
                user=request.user,
                product=product
            )
            if created:
                return Response(
                    {"message": "You’ll be notified when this product becomes available."},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response({"message": "You’re already subscribed for this product."})
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)