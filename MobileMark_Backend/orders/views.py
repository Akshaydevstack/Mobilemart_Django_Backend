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

    # ✅ Replace your old create() with this one
    def create(self, request, *args, **kwargs):
        data = request.data
        payment_method = data.get("payment_method")

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)

        # ✅ Save Razorpay info if applicable
        if payment_method == "Razorpay":
            order.razorpay_payment_id = data.get("razorpay_payment_id")
            order.razorpay_order_id = data.get("razorpay_order_id")
            order.razorpay_signature = data.get("razorpay_signature")
            order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

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
        try:
            data = json.loads(request.body)
            amount = int(data.get("amount", 0)) * 100  # amount in paise
            if amount <= 0:
                return JsonResponse({"error": "Invalid amount"}, status=400)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            order = client.order.create(dict(amount=amount, currency="INR", payment_capture=1))
            return JsonResponse(order)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)