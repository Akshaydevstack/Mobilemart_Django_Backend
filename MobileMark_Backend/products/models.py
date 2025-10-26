from django.db import models
from brands.models import Brand
from django.contrib.auth import get_user_model
# Create your models here.
class Product(models.Model):
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    upcoming = models.BooleanField(default=False)  # ✅ New field
    count = models.IntegerField(default=15)
    def __str__(self):
        return f"{self.brand} - {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f"Image for {self.product.name}"


User = get_user_model()

class ProductReview(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    username = models.CharField(max_length=255)  # store username for quick access
    rating = models.IntegerField(default=5)      # 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.username} for {self.product.name}"