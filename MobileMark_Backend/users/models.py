from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    # Use email as the unique login field
    email = models.EmailField(unique=True)

    # Optional user role
    role = models.CharField(max_length=20, default="User")
    is_block = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Fix reverse accessor clashes with default auth.User
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )

    # Normal name field (optional, can be blank)
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=False,
    )

    # Use email as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No other fields required for createsuperuser

    def __str__(self):
        return self.username if self.username else self.email

    # Helper for Google OAuth: allow users without password
    def set_unusable_password(self):
        super().set_unusable_password()
        self.save()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)  # optional: to mark one as default
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.city}"