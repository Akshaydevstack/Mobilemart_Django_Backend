from django.urls import path
from .views import BannerOfferView
from .views import AdminCouponManagementView

urlpatterns = [
    path('admin/banner-management/', BannerOfferView.as_view(), name='banner-list-created'),          # GET, POST
    path('admin/banner-management/<int:offer_id>/', BannerOfferView.as_view(), name='banner-update-delete'),  # PATCH, DELETE
    path('admin/coupons-management/', AdminCouponManagementView.as_view(), name='coupon-list-created'),
    path('admin/coupons-management/<int:pk>/', AdminCouponManagementView.as_view(), name='coupon-update-delete'),
]