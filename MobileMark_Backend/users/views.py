from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings


User = get_user_model()

# Registration view (auto-login)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate refresh token
        refresh = RefreshToken.for_user(user)

        # Prepare response with access token
        response = Response(serializer.data, status=status.HTTP_201_CREATED)

        # Set refresh token in HttpOnly cookie
        response.set_cookie(
           key="refresh_token",
                value= str(refresh),
                httponly=True,
                secure=False,  # True in production (HTTPS)
                samesite="Lax",
                path="/", 
                max_age=7*24*60*60  # 7 days
        )

        return response



# Login view using custom JWT

class CustomLoginView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Use the custom serializer to get the token with extra claims
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            access = refresh.access_token

            response = Response({
                "access": str(access),
            }, status=200)

            # Set refresh token in HttpOnly cookie
            response.set_cookie(
               key="refresh_token",
                value= str(refresh),
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
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify token with Google
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)

            email = idinfo.get("email")
            name = idinfo.get("name", "")
            google_id = idinfo.get("sub")

            # Check if user exists, otherwise create
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": name}
            )

            # Set unusable password for new users
            if created:
                user.set_unusable_password()
                user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = CustomTokenObtainPairSerializer.get_token(user).access_token

            # Set refresh token in HttpOnly cookie
            response = Response({
                "access": str(access_token)
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                key="refresh_token",
                value= str(refresh),
                httponly=True,
                secure=False,  # True in production (HTTPS)
                samesite="Lax",
                path="/", 
                max_age=7*24*60*60  # 7 days
            )

            return response

        except ValueError as e:
            print("Google Auth Error:", e)
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Google Auth Error:", e)
            return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # print("COOKIES:", request.COOKIES)
        refresh_token = request.COOKIES.get("refresh_token")  # ✅ from cookies now
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


class TestView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        return Response({"message":"authenticaton done!"})
