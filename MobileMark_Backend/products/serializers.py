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

    def create(self, validated_data):
        brand_data = validated_data.pop('brand')
        images = validated_data.pop('images', [])

        # ✅ Get or create the brand
        brand, _ = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults={'description': brand_data.get('description', '')}
        )

        # ✅ Atomic creation of product + images
        with transaction.atomic():
            product = Product.objects.create(brand=brand, **validated_data)
            if images:
                ProductImage.objects.bulk_create([
                    ProductImage(product=product, image_url=url) for url in images
                ])

        return product

    def update(self, instance, validated_data):
        brand_data = validated_data.pop('brand', None)
        images = validated_data.pop('images', None)

        # ✅ Update brand if provided
        if brand_data:
            brand, _ = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={'description': brand_data.get('description', '')}
            )
            instance.brand = brand

        # ✅ Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # ✅ Replace images if provided
        if images is not None:
            instance.images.all().delete()  # clear old images
            ProductImage.objects.bulk_create([
                ProductImage(product=instance, image_url=url) for url in images
            ])

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['images'] = [img.image_url for img in instance.images.all()]
        return data