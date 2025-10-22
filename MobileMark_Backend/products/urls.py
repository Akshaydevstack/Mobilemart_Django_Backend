from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,ProductReviewCreateView,ProductReviewListView
from django.urls import path,include


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path("", include(router.urls)),
    path('reviews/', ProductReviewListView.as_view(), name='product-review-list'),
    path('reviews/create/', ProductReviewCreateView.as_view(), name='product-review-create')
]