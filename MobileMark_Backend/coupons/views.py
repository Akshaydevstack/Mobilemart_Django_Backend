from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import BannerOffer
from .serializers import BannerOfferSerializer
from .models import Coupon
from .serializers import CouponSerializer


class BannerOfferView(APIView):

    def get(self, request, offer_id=None):
    # List all active offers if no offer_id is provided
        if not offer_id:
            offers = BannerOffer.objects.filter(is_active=True).order_by('-created_at')
            serializer = BannerOfferSerializer(offers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Retrieve a single offer by ID
        try:
            offer = BannerOffer.objects.get(id=offer_id)
        except BannerOffer.DoesNotExist:
            return Response(
                {"error": "Offer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BannerOfferSerializer(offer)
        return Response(serializer.data, status=status.HTTP_200_OK)
            
        

    def post(self, request):
        # Create a new offer
        serializer = BannerOfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, offer_id):
        # Update existing offer
        offer = get_object_or_404(BannerOffer, id=offer_id)
        serializer = BannerOfferSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, offer_id):
        # Delete existing offer
        offer = get_object_or_404(BannerOffer, id=offer_id)
        offer.delete()
        return Response({"detail": "Offer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    



class AdminCouponManagementView(APIView):
    """
    Admin view to manage coupons
    """

    def get(self, request):
        coupons = Coupon.objects.all().order_by('-created_at')
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            coupon = Coupon.objects.get(pk=pk)
        except Coupon.DoesNotExist:
            return Response({"error": "Coupon not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CouponSerializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            coupon = Coupon.objects.get(pk=pk)
        except Coupon.DoesNotExist:
            return Response({"error": "Coupon not found"}, status=status.HTTP_404_NOT_FOUND)
        coupon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)