from rest_framework import serializers
from .models import Wishlist
from products.models import Product, ProductImage



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image_url"]



class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "images",
            "count",
            "description",
            "brand",
            "brand_name",
        ]

    def get_images(self, obj):
        # Return only the image_url as a list of strings
        return [img.image_url for img in obj.images.all()]


class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "user", "products", "created_at"]