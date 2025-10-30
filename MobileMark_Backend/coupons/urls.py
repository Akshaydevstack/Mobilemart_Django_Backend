from django.urls import path
from .views import BannerOfferView
from .views import AdminCouponManagementView

urlpatterns = [
    path('admin/banner/', BannerOfferView.as_view(), name='banner-list-created'),          # GET, POST
    path('admin/banner/<int:offer_id>/', BannerOfferView.as_view(), name='banner-update-delete'),  # PATCH, DELETE
    path('admin/coupons/', AdminCouponManagementView.as_view(), name='coupon-list-created'),
    path('admin/coupons/<int:pk>/', AdminCouponManagementView.as_view(), name='coupon-update-delete'),
]