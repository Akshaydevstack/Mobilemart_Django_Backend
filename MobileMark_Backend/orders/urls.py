from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, create_order
from django.urls import path , include

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")


urlpatterns = [
    path("",include(router.urls)),
    path("create-order/", create_order, name="create_order"),
]