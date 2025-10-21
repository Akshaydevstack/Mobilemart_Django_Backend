# cart/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product


# ✅ Product Serializer (with image URLs only)
class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    class Meta:
        model = Product
        fields = ["id", "name", "price", "images", "count", "description", "brand","brand_name"]

    def get_images(self, obj):
        # return list of URLs only
        return [img.image_url for img in obj.images.all()]


# ✅ CartItem Serializer
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal


# ✅ Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total"]

    def get_total(self, obj):
        return obj.total()