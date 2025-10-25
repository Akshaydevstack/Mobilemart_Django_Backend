from rest_framework import serializers
from brands.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'product_count']

    def get_product_count(self, obj):
        # Assumes your Product model has a ForeignKey to Brand named 'brand'
        return obj.products.count()  # obj.products is the related_name in Product model

    def create(self, validated_data):
        # ✅ Avoid duplicate brand error
        brand, _ = Brand.objects.get_or_create(
            name=validated_data['name'],
            defaults={'description': validated_data.get('description', '')}
        )
        return brand
