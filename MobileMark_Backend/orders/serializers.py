from rest_framework import serializers
from .models import Order, OrderItem, ShippingInfo
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "product_image", "quantity", "price"]

    def get_product_image(self, obj):
        images = obj.product.images.all()
        if images.exists():
            return images[0].image_url
        return None


class ShippingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingInfo
        fields = ["name", "email", "phone", "address", "city", "state", "zip_code"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    shipping_info = ShippingInfoSerializer()
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user_name",
            "subtotal",
            "discount",
            "total",
            "payment_method",
            "status",
            "created_at",
            "items",
            "shipping_info",
        ]
        read_only_fields = ["status", "created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        shipping_data = validated_data.pop("shipping_info")

        # ✅ Automatically assign user from request context
        user = self.context["request"].user
        validated_data["user"] = user

        # ✅ Create the order
        order = Order.objects.create(**validated_data)

        # ✅ Create each order item
        for item_data in items_data:
            product_id = item_data.get("product")
            try:
                product = Product.objects.get(id=product_id.id if hasattr(product_id, "id") else product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product": f"Product with ID {product_id} not found."})

            OrderItem.objects.create(order=order, product=product, quantity=item_data["quantity"], price=item_data["price"])

        # ✅ Create shipping info
        ShippingInfo.objects.create(order=order, **shipping_data)

        return order