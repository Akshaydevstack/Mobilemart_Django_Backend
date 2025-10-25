from rest_framework.routers import DefaultRouter
from .views import CartViewSet , AdminManageCartView,ProductCartCountView
from django.urls import path,include
router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")


urlpatterns = [
    path("", include(router.urls)),
    path("admin/cart-management/", AdminManageCartView.as_view(),name='admin-mangecart'),
    path("admin/cart-management/<int:user_id>/", AdminManageCartView.as_view(),name='admin-mangecart'),
    path("admin/product-cart-countView",ProductCartCountView.as_view(),name='admin-product-count')
   ]