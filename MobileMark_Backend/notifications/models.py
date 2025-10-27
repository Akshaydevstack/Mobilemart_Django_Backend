from django.db import models
from users.models import User
from django.db import models
from products.models import Product 

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    title = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title or f"Notification {self.id}"
    


class ProductNotificationSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_notifications")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="subscribers")
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)  

    class Meta:
        unique_together = ('user', 'product')  
    def __str__(self):
        return f"{self.user.email} -> {self.product.name}"