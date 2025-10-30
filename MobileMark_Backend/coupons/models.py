from django.db import models
from django.utils import timezone


class BannerOffer(models.Model):
    message = models.TextField(help_text="The offer message to display in the banner.")
    is_active = models.BooleanField(default=True, help_text="Only active offers will be shown.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:50]  
    

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=10,
        choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage'
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

    def __str__(self):
        return self.code