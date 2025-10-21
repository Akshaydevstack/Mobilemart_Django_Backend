from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer
import razorpay
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class OrderViewSet(viewsets.ModelViewSet):
    """
    Handles creating, listing, retrieving, and updating orders.
    Only authenticated users can create orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ["Delivered", "Cancelled"]:
            return Response({"error": "Cannot cancel this order"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = "Cancelled"
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    



@csrf_exempt
def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount = int(data.get("amount", 500)) * 100  # Razorpay works in paise
        currency = "INR"

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create order
        order = client.order.create(dict(amount=amount, currency=currency, payment_capture=1))

        return JsonResponse(order)