from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now
from users.models import User
from products.models import Product
from orders.models import Order
from cart.models import Cart, CartItem
from common.permissions import IsAdminUserRole

# Create your views here.

class DashboardOverviewView(APIView):

    permission_classes = [IsAdminUserRole]

    def get(self, request):
        today = now().date()

        # USERS
        total_users = User.objects.count()
        new_users_this_month = User.objects.filter(date_joined__month=today.month).count()
        pending_approvals = User.objects.filter(is_block=True).count()

        # PRODUCTS
        total_products = Product.objects.count()
        new_products = Product.objects.filter(created_at__month=today.month).count()
        out_of_stock = Product.objects.filter(count=0).count()

        # ORDERS
        total_orders = Order.objects.count()
        pending_shipments = Order.objects.filter(status="Pending").count()
        Processing = Order.objects.filter(status="Processing").count()

        # CARTS
        total_cart_items = CartItem.objects.count()
        new_items_today = CartItem.objects.filter(added_date__date=today).count()
        abandoned_carts = Cart.objects.count()

        data = {
            "users": {
                "total": total_users,
                "new_this_month": new_users_this_month,
                "pending_approvals": pending_approvals,
            },
            "products": {
                "total": total_products,
                "new_listings": new_products,
                "out_of_stock": out_of_stock,
            },
            "orders": {
                "total": total_orders,
                "pending_shipments": pending_shipments,
                "Processing": Processing,
            },
            "carts": {
                "total_items": total_cart_items,
                "items_added_today": new_items_today,
                "abandoned_carts":abandoned_carts                 
            },
        }

        return Response(data)