from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet,AdminMangeWishlistView
from django.urls import path,include
router = DefaultRouter()
router.register(r"wishlist", WishlistViewSet, basename="wishlist")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/wishlist-management/", AdminMangeWishlistView.as_view(),name= 'wishlist-management'),
    path("admin/wishlist-management/<int:user_id>/", AdminMangeWishlistView.as_view(),name= 'wishlist-management')
]