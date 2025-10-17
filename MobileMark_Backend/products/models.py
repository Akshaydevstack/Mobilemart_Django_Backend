from django.db import models
from brands.models import Brand

# Create your models here.
class Product(models.Model):
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField(default=15)
    def __str__(self):
        return f"{self.brand} - {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f"Image for {self.product.name}"