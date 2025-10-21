from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist
from products.models import Product
from .serializers import WishlistSerializer


class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)

    def create(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=404)

        if product in wishlist.products.all():
            return Response({"detail": "Product already in wishlist"}, status=400)

        wishlist.products.add(product)
        return Response({"detail": "Added to wishlist"}, status=201)

    def destroy(self, request, pk=None):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=404)

        wishlist.products.remove(product)
        return Response({"detail": "Removed from wishlist"}, status=204)