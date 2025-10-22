from django.urls import path
from .views import RegisterView, CustomLoginView, LogoutView,CurrentUserView, UserSelfUpdateView, UserBlockUpdateView,ChangeEmailView
from .views import   GoogleLoginView, CookieTokenRefreshView, PasswordResetConfirmView, PasswordResetView,ChangePasswordView
from .views import AddressListCreateView,AddressDetailView,DeleteUserView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(),name="password-reset-confirm"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("me/update/", UserSelfUpdateView.as_view(), name="user-self-update"),
    path("me/block/<int:id>/",UserBlockUpdateView.as_view(), name="admin-user-block"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path('change-email/', ChangeEmailView.as_view(), name='change-email'),
    path("addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
    path('<int:pk>/delete/', DeleteUserView.as_view(), name='delete_user'),
]
  

