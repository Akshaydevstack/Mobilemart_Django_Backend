from rest_framework import serializers
from .models import BannerOffer
from .models import Coupon


class BannerOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerOffer
        fields = ['id', 'message', 'is_active', 'created_at']



class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = '__all__'

    def get_is_valid(self, obj):
        return obj.is_valid()