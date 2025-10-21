from rest_framework import serializers
from django.db import transaction
from .models import Product, ProductImage
from brands.models import Brand
from brands.serializers import BrandSerializer


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    images = serializers.ListField(
        child=serializers.URLField(),
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'brand', 'name', 'price', 'description', 'is_active', 'count', 'images', 'created_at']

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

    def to_representation(self, instance):
        # ✅ Customize output: images as list of URLs
        data = super().to_representation(instance)
        data['images'] = [img.image_url for img in instance.images.all()]
        return data


