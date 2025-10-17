from rest_framework import serializers
from django.db import transaction
from products.models import Product, ProductImage
from brands.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description']

    def create(self, validated_data):
        # ✅ Avoid duplicate brand error
        brand, _ = Brand.objects.get_or_create(
            name=validated_data['name'],
            defaults={'description': validated_data.get('description', '')}
        )
        return brand