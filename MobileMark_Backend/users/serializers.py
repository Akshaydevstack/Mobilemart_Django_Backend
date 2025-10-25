from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import viewsets
from .models import Address
User = get_user_model()


# Custom JWT to include extra info
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = getattr(user, 'role', 'User')
        token['is_block'] = user.is_block
        return token


# Registration serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # Create user
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        # Generate JWT tokens
        refresh = RefreshToken.for_user(instance)
        access = refresh.access_token

        # Add custom claims to access token
        access['user_id'] = instance.id
        access['username'] = instance.username
        access['email'] = instance.email
        access['role'] = getattr(instance, 'role', 'User')
        access['is_block'] = instance.is_block

        return {
            'access': str(access)
        }


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=6)



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "role",
            "is_block",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "email", "created_at", "is_active"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "is_default",
        ]

