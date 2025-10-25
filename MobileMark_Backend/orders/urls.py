from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, create_order ,AdminOrderManagementView , BrandSalesReportView,AdminBusinessAnalyticsView,DailySalesView
from django.urls import path , include

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")


urlpatterns = [
    path("",include(router.urls)),
    path("create-order/", create_order, name="create_order"),
    path("admin/order-management/",AdminOrderManagementView.as_view(),name='mange_user_orders'),
    path("admin/order-management/<int:user_id>/",AdminOrderManagementView.as_view(),name='mange_user_orders'),
    path("admin/brand-sales-report/",BrandSalesReportView.as_view(),name="brand_sales_report"),
    path("admin/business-analytics/", AdminBusinessAnalyticsView.as_view(),name="business_analytics" ),
    path('admin/daily-sales/', DailySalesView.as_view(), name='daily-sales')
]