from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer
import razorpay
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.db.models import Q, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer,AdminTotalOrderSerializer
from django.db.models import Sum, F, Q
from .models import OrderItem
from users.models import User
from django.db.models import Prefetch, Q
from rest_framework.pagination import PageNumberPagination
from django.db.models.functions import ExtractHour
from datetime import datetime
from decimal import Decimal
from .models import Order
from django.db.models.functions import TruncMonth


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user).order_by("created_at")

    def create(self, request, *args, **kwargs):
        data = request.data
        payment_method = data.get("payment_method")

        serializer = self.get_serializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)

        # ✅ Save Razorpay info if applicable
        if payment_method == "Razorpay":
            order.razorpay_payment_id = data.get("razorpay_payment_id")
            order.razorpay_order_id = data.get("razorpay_order_id")
            order.razorpay_signature = data.get("razorpay_signature")
            order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ["Delivered", "Cancelled"]:
            return Response({"error": "Cannot cancel this order"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = "Cancelled"
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount = int(data.get("amount", 0)) * 100  # amount in paise
            if amount <= 0:
                return JsonResponse({"error": "Invalid amount"}, status=400)

            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            order = client.order.create(
                dict(amount=amount, currency="INR", payment_capture=1))
            return JsonResponse(order)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)


# admin only view

class AdminOrderManagementView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id=None):
        orders_qs = Order.objects.all()

        if user_id is not None:
            orders_qs = orders_qs.filter(user__id=user_id)

        stats = orders_qs.values("status").annotate(count=Count("id"))
        stats_dict = {s["status"].lower(): s["count"] for s in stats}
        stats_dict["all"] = orders_qs.count()
        for key in ["pending", "processing", "delivered", "cancelled"]:
            stats_dict.setdefault(key, 0)

        search = request.query_params.get("search", "")
        status_filter = request.query_params.get("status", "")
        date_filter = request.query_params.get("date", "")
        ordering = request.query_params.get("ordering", "-created_at")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        if search:
            orders_qs = orders_qs.filter(
                Q(user__username__icontains=search) |
                Q(status__icontains=search) |
                Q(payment_method__icontains=search) |
                Q(shipping_info__city__icontains=search) |
                Q(id__exact=search)
            )

        if status_filter and status_filter.lower() != "all":
            orders_qs = orders_qs.filter(status__iexact=status_filter)

        if date_filter:
            orders_qs = orders_qs.filter(created_at__date=date_filter)

        orders_qs = orders_qs.order_by(ordering)

        paginator = Paginator(orders_qs, page_size)
        page_obj = paginator.get_page(page)

        serializer = OrderSerializer(page_obj, many=True)

        query_params = request.GET.copy()
        base_url = request.build_absolute_uri(request.path)

        def build_url(page_number):
            query_params["page"] = page_number
            return f"{base_url}?{query_params.urlencode()}"

        next_page = build_url(page_obj.next_page_number()
                              ) if page_obj.has_next() else None
        previous_page = build_url(
            page_obj.previous_page_number()) if page_obj.has_previous() else None

        return Response({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "stats": stats_dict,
            "current_page": page_obj.number,
            "next": next_page,
            "previous": previous_page,
            "results": serializer.data,
        }, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        try:
            order = Order.objects.get(id=user_id)
        except Order.DoesNotExist:
            return Response({"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "Status field is required"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save(update_fields=["status"])

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)




class BrandSalesReportView(APIView):
    def get(self, request):

        data = (
            OrderItem.objects
            .filter(~Q(order__status="Cancelled"))
            .select_related("order", "product__brand")
            .values("product__brand__name")
            .annotate(
                total_quantity_sold=Sum("quantity"),
                total_revenue=Sum(F("quantity") * F("price")),
                total_orders=Count("order", distinct=True)
            )
            .order_by("-total_revenue")
        )

        summary = {
            "total_brands": data.count(),
            "overall_quantity_sold": sum(item["total_quantity_sold"] for item in data),
            "overall_revenue": sum(item["total_revenue"] for item in data),
        }

        return Response({
            "summary": summary,
            "brands": data
        })




class AdminBusinessAnalyticsView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        order_filter = Q()
        if start_date:
            order_filter &= Q(created_at__date__gte=start_date)
        if end_date:
            order_filter &= Q(created_at__date__lte=end_date)

        orders = Order.objects.filter(order_filter).select_related('user').order_by('-created_at')

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(orders, request)
        serializer = AdminTotalOrderSerializer(result_page, many=True)

        # Base stats
        total_sales = orders.aggregate(total_sales=Sum('total'))['total_sales'] or 0
        total_orders = orders.count()
        avg_order_value = round(total_sales / total_orders, 2) if total_orders > 0 else 0

        # Order statuses
        completed_orders = orders.filter(status="Delivered").count()
        cancelled_orders = orders.filter(status="Cancelled").count()
        returned_orders = orders.filter(status="Returned").count()
        pending_orders = orders.filter(status="Pending").count()

        # Customer insights
        unique_customers = orders.values('user').distinct().count()
        repeat_customers = (
            orders.values('user')
            .annotate(order_count=Count('id'))
            .filter(order_count__gte=2)
            .count()
        )

        # Daily sales
        daily_sales_qs = (
            orders.extra({'date': "date(created_at)"})
            .values('date')
            .annotate(daily_total=Sum('total'))
            .order_by('date')
        )
        daily_sales = {item['date'].isoformat(): float(item['daily_total']) for item in daily_sales_qs}

        # Monthly sales (for charts)
        monthly_sales_qs = (
            orders.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(monthly_total=Sum('total'))
            .order_by('month')
        )
        monthly_sales = {item['month'].strftime("%Y-%m"): float(item['monthly_total']) for item in monthly_sales_qs}

        # Best-selling products (top 5)
        best_selling_products = (
            OrderItem.objects
            .filter(order__in=orders)
            .values('product__name')
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:5]
        )

        response_data = {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data,

            'chart_data': {
                'total_sales': float(total_sales),
                'total_orders': total_orders,
                'average_order_value': avg_order_value,
                'daily_sales': daily_sales,
                'monthly_sales': monthly_sales,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'returned_orders': returned_orders,
                'pending_orders': pending_orders,
                'unique_customers': unique_customers,
                'repeat_customers': repeat_customers,
                'best_selling_products': list(best_selling_products),
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)




class DailySalesView(APIView):
    def get(self, request):

        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "Date parameter is required (YYYY-MM-DD)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        
        orders = Order.objects.filter(
            created_at__date=selected_date
        ).exclude(status="Cancelled")

        
        hourly_data = (
            orders.annotate(hour=ExtractHour("created_at"))
            .values("hour")
            .annotate(
                total_revenue=Sum("total"),
                order_count=Count("id")
            )
            .order_by("hour")
        )

        
        hourly_sales = []
        for h in hourly_data:
            revenue = h["total_revenue"] or Decimal(0)
            profit = revenue * Decimal("0.25")  # 25% profit
            hourly_sales.append({
                "hour": f"{h['hour']:02d}:00",
                "orders": h["order_count"],
                "revenue": float(revenue),
                "profit": float(profit)
            })

        
        total_revenue = orders.aggregate(Sum("total"))["total__sum"] or Decimal(0)
        total_profit = total_revenue * Decimal("0.25")
        total_orders = orders.count()

        daily_totals = {
            "orders": total_orders,
            "revenue": float(total_revenue),
            "profit": float(total_profit),
            "avgOrderValue": float(total_revenue / total_orders) if total_orders > 0 else 0,
            "avgProfitPerOrder": float(total_profit / total_orders) if total_orders > 0 else 0
        }

        return Response({
            "date": selected_date,
            "hourly_sales": hourly_sales,
            "daily_totals": daily_totals
        }, status=status.HTTP_200_OK)