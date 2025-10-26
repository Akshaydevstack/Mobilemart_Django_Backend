from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Product
from rest_framework.views import APIView
from django.db.models import Count
from django.utils.timezone import now
from users.models import User
from orders.models import Order


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # GET /cart/ -> get user's cart
    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    

    # POST /cart/ -> add/update product in cart
    def create(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # PATCH /cart/<cart_item_id>/ -> update quantity
    def partial_update(self, request, pk=None):
        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)
        quantity = int(request.data.get("quantity", 1))
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartSerializer(cart_item.cart)
        return Response(serializer.data)

    # DELETE /cart/<cart_item_id>/ -> remove item
    def destroy(self, request, pk=None):
        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # DELETE /cart/clear/ -> clear entire cart
    @action(detail=False, methods=["delete"])
    def clear(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared"})
    


# admin only view 

class AdminManageCartView(APIView):

    def get(self,request,user_id=None):
        if not user_id:
            carts = Cart.objects.filter(items__isnull=False).distinct()
            serializer = CartSerializer(carts,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            try:
                cart = Cart.objects.get(user_id = user_id)
                serializer= CartSerializer(cart)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except Cart.DoesNotExist:
                return Response({"error":"No cart exixt"})



class ProductCartCountView(APIView):
    def get(self, request):
        data = (
            CartItem.objects
            .select_related('product', 'product__brand')  # prefetch related objects
            .values(
                "product",
                "product__name",
                "product__price",
                "product__brand__name"
            )
            .annotate(total_cart_count=Count("cart", distinct=True))
            .order_by("-total_cart_count")
        )
        return Response(data)
    



