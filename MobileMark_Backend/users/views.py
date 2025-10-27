from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from rest_framework.settings import api_settings
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from rest_framework import generics, permissions
from .models import Address
from .serializers import AddressSerializer
from rest_framework import viewsets
from django.db.models import Q
from common.permissions import IsAdminUserRole


User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # ✅ Generate both tokens
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        access = refresh.access_token

        # ✅ Include access token in response
        response = Response(
            {
                "access": str(access),
                "user": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

        # ✅ Store refresh token as cookie (same as Google login)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,  # True in production (HTTPS)
            samesite="Lax",  # Lax works with local dev + cookie sending
            path="/",
            max_age=7 * 24 * 60 * 60  # 7 days
        )

        return response


class CustomLoginView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            access = refresh.access_token

            response = Response({
                "access": str(access),
            }, status=200)

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,  # True in production (HTTPS)
                samesite="Lax",
                path="/",
                max_age=7*24*60*60  # 7 days
            )

            return response
        else:
            return Response({"detail": "Invalid credentials"}, status=401)


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        try:
            # Verify token
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            email = idinfo.get("email")
            name = idinfo.get("name", "")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": name}
            )

            if created:
                user.set_unusable_password()
                user.save()

            # Create tokens
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            access_token = refresh.access_token

            # Set refresh token cookie
            response = Response({
                "access": str(access_token)
            }, status=200)

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,   # Local dev
                samesite="Lax",  # ✅ Must be Lax for local testing
                path="/",
                max_age=7*24*60*60
            )

            return response

        except Exception as e:
            print("Google Auth Error:", e)
            return Response({"error": "Google login failed"}, status=400)


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            print(refresh_token)
            return Response({"detail": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = RefreshToken(refresh_token)
            data = {"access": str(token.access_token)}
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Token invalid or expired"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(
            "refresh_token")  # ✅ from cookies now
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Requires blacklist app
        except TokenError:
            return Response({"error": "Invalid or expired refresh token"}, status=400)

        response = Response({"detail": "Logout successful"}, status=205)
        # Optional: Clear cookies after logout
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal user existence
            return Response({"success": True}, status=status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        # React frontend URL
        reset_url = f"http://localhost:5173/reset-password/{uid}/{token}/"

        # Send email
        subject = "Password Reset Request"
        message = f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_url}\n\nIf you did not request this, ignore this email."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  [user.email], fail_silently=False)

        return Response({"success": True}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data["uidb64"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"success": "Password reset successful"}, status=status.HTTP_200_OK)


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserSelfUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()

        allowed_fields = ["username", "email"]
        data = {field: request.data[field]
                for field in allowed_fields if field in request.data}

        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserBlockUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        is_block = request.data.get("is_block")

        if is_block is None:
            return Response({"error": "is_block field is required"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_block = is_block
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not user.check_password(old_password):
            return Response({"old_password": "Incorrect current password."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"confirm_password": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password updated successfully!"}, status=status.HTTP_200_OK)


class ChangeEmailView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        new_email = request.data.get("new_email")
        confirm_email = request.data.get("confirm_email")

        if not new_email or not confirm_email:
            return Response({"detail": "Both email fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if new_email != confirm_email:
            return Response({"detail": "Emails do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if email already exists
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=new_email).exists():
            return Response({"detail": "This email is already in use."}, status=status.HTTP_400_BAD_REQUEST)

        user.email = new_email
        user.save()

        return Response({"detail": "Email updated successfully!"}, status=status.HTTP_200_OK)


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)





# Admin only view

class AdminManageUsersView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request, pk=None):
        if pk is None:

            total_users = User.objects.count()
            blocked_users = User.objects.filter(is_block=True).count()
            admin_users = User.objects.filter(role='Admin').count()

            users = User.objects.all().order_by('-id')

            search = request.query_params.get('search')
            role = request.query_params.get('role')
            is_block = request.query_params.get('is_block')

            if search:
                if search.isdigit():
                    users = users.filter(
                        Q(username__icontains=search) |
                        Q(email__icontains=search) |
                        Q(id=int(search))
                    )
                else:
                    users = users.filter(
                        Q(username__icontains=search) |
                        Q(email__icontains=search)
                    )

            if role:
                users = users.filter(role=role)

            if is_block is not None:
                if is_block.lower() == 'true':
                    users = users.filter(is_block=True)
                elif is_block.lower() == 'false':
                    users = users.filter(is_block=False)

            paginator_class = api_settings.DEFAULT_PAGINATION_CLASS
            paginator = paginator_class()
            paginator.page_size = 18
            paginated_users = paginator.paginate_queryset(users, request)
            serializer = UserSerializer(paginated_users, many=True)

            response = paginator.get_paginated_response(serializer.data)
            response.data.update({
                "total_users": total_users,
                "blocked_users": blocked_users,
                "admin_users": admin_users,
            })

            return response

    def patch(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"error": "user not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": f"User {user.username} deleted successfully"}, status=status.HTTP_200_OK)
