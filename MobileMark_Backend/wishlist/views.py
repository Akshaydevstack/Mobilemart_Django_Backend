from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Wishlist
from products.models import Product
from .serializers import WishlistSerializer
from rest_framework.views import APIView


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





# admin only

class AdminMangeWishlistView(APIView):
    permission_classes = [AllowAny]
    def get(self,request,user_id=None):
        if not user_id:
            wishlists = Wishlist.objects.all()
            serializer = WishlistSerializer(wishlists, many = True)
            return Response(serializer.data,status= status.HTTP_200_OK)
        else:
            try:
                wishlist = Wishlist.objects.get(user_id = user_id)
                serializer = WishlistSerializer(wishlist)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except Wishlist.DoesNotExist:
                wishlist = Wishlist.objects.create(user_id=user_id)
                serializer = WishlistSerializer(wishlist)
                return Response(serializer.data, status=status.HTTP_201_CREATED)