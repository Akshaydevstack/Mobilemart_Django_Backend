from rest_framework import serializers
from django.db import transaction
from .models import Product, ProductImage,ProductReview
from brands.models import Brand
from brands.serializers import BrandSerializer


class ProductReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'username', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'username', 'created_at']



class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    images = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False
    )
    reviews = ProductReviewSerializer(many=True, read_only=True)  # nested reviews

    class Meta:
        model = Product
        fields = ['id', 'brand', 'name', 'price', 'description', 'is_active', 'count', 'images', 'created_at', 'reviews']


    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['images'] = [img.image_url for img in instance.images.all()]
        return data






class AdminProductSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        write_only=True
    )
    brand_detail = BrandSerializer(source='brand', read_only=True)

    images = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False
    )
    image_urls = serializers.SerializerMethodField()
    reviews = ProductReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'brand', 'brand_detail', 'name', 'price', 'description',
            'is_active','upcoming','count', 'images', 'image_urls', 'created_at', 'reviews'
        ]

    @transaction.atomic
    def create(self, validated_data):
        brand = validated_data.pop('brand')
        images_data = validated_data.pop('images', [])

        # ✅ Create product
        product = Product.objects.create(brand=brand, **validated_data)

        # ✅ Create multiple product images
        for url in images_data:
            ProductImage.objects.create(product=product, image_url=url)

        return product

    def get_image_urls(self, obj):
        """Return list of all image URLs for the product."""
        return [img.image_url for img in obj.images.all()]