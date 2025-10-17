from django.urls import path
from .views import RegisterView, CustomLoginView , TestView,LogoutView,GoogleLoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login')
]