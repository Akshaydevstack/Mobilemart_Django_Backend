from django.urls import path
from .views import RegisterView, CustomLoginView, LogoutView,CurrentUserView, UserSelfUpdateView, UserBlockUpdateView,ChangeEmailView
from .views import   GoogleLoginView, CookieTokenRefreshView, PasswordResetConfirmView, PasswordResetView,ChangePasswordView
from .views import AddressListCreateView,AddressDetailView,AdminManageUsersView



urlpatterns = [
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/login/', CustomLoginView.as_view(), name='login'),
    path('users/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('users/logout/', LogoutView.as_view(), name='logout'),
    path('users/google-login/', GoogleLoginView.as_view(), name='google-login'),
    path("users/password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("users/password-reset-confirm/", PasswordResetConfirmView.as_view(),name="password-reset-confirm"),
    path("users/me/", CurrentUserView.as_view(), name="current-user"),
    path("users/me/update/", UserSelfUpdateView.as_view(), name="user-self-update"),
    path("users/me/block/<int:id>/",UserBlockUpdateView.as_view(), name="admin-user-block"),
    path("users/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path('users/change-email/', ChangeEmailView.as_view(), name='change-email'),
    path("users/addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("users/addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
    path("admin/users-management/", AdminManageUsersView.as_view(), name="users-management"),
    path("admin/users-management/<int:pk>/", AdminManageUsersView.as_view(), name="users-management"),
    
]
  

