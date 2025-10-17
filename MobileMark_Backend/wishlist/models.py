from django.db import models
from users.models import User
from products.models import Product
# Create your models here.

class Wishlist(models.Model):
    user = models.OneToOneField(User, related_name="wishlist", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)