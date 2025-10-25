from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,ProductReviewCreateView,ProductReviewListView,AdminProductManagementView
from django.urls import path,include


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path("", include(router.urls)),
    path('reviews/', ProductReviewListView.as_view(), name='product-review-list'),
    path('reviews/create/', ProductReviewCreateView.as_view(), name='product-review-create'),
    path('admin/manage-products/',AdminProductManagementView.as_view(),name='manage-products'),
    path('admin/manage-products/<int:product_id>/', AdminProductManagementView.as_view(), name='admin_manage_product_detail'),
]