from rest_framework.response import Response
from .serializers import ProductSerializer
from rest_framework import viewsets, permissions, status, filters, generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductReview, Product,ProductImage
from .serializers import ProductReviewSerializer,AdminProductSerializer
from rest_framework.views import APIView
from django.db.models import Q,F
from brands.models import Brand
from brands.serializers import BrandSerializer
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('brand').prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'brand__id': ['exact'],     
        'is_active': ['exact'],     
        'price': ['gte', 'lte'],    
    }
    
    search_fields = ['name', 'description', 'brand__name']

    ordering_fields = ['price', 'created_at', 'name']

    ordering = ['id']  



# ✅ GET - List all reviews for a specific product
class ProductReviewListView(generics.ListAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return ProductReview.objects.filter(product_id=product_id).order_by('-created_at')
        return ProductReview.objects.none()


# ✅ POST - Create a new review
class ProductReviewCreateView(generics.CreateAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        product = Product.objects.get(id=product_id)
        serializer.save(user=self.request.user, product=product)




class AdminProductManagementView(APIView):
    """
    Admin API for managing products:
    - GET: List products or brands, optionally filter by stock
    - POST: Create product with images
    - PATCH: Update product and optionally replace images
    - DELETE: Delete product
    """

    def get(self, request):
        # Get all brands
        if request.query_params.get("brands") == "true":
            brands = Brand.objects.all()
            serializer = BrandSerializer(brands, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Product listing
        products_qs = Product.objects.all()
        brand_id = request.query_params.get("brand_id")
        search = request.query_params.get("search", "")
        ordering = request.query_params.get("ordering", "-created_at")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        stock_filter = request.query_params.get("stock")  # 'low' or 'out'
        active_filter= request.query_params.get("active")

        total_products = Product.objects.all().count()
        active_products = Product.objects.filter(is_active=True).count()
        outofstock = Product.objects.filter(count=0).count()
        lowstock = Product.objects.filter(count__lt=10,count__gt=0).count()
        inactive = Product.objects.filter(is_active=False).count()
 
        # Brand filter
        if brand_id:
            products_qs = products_qs.filter(brand__id=brand_id)

        # Search filter
        if search:
            products_qs = products_qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search)
            )

        # Stock filter
        if stock_filter == "low":
            products_qs = products_qs.filter(count__lt=10,count__gt=0)
        elif stock_filter == "out":
            products_qs = products_qs.filter(count=0)

        if active_filter == "active":
            products_qs = products_qs.filter(is_active=True)
        elif active_filter == "inactive" :
            products_qs = products_qs.filter(is_active=False)
            

        products_qs = products_qs.order_by(ordering)

        paginator = Paginator(products_qs, page_size)
        page_obj = paginator.get_page(page)
        serializer = AdminProductSerializer(page_obj, many=True)

        query_params = request.GET.copy()
        base_url = request.build_absolute_uri(request.path)
        def build_url(page_number):
            query_params["page"] = page_number
            return f"{base_url}?{query_params.urlencode()}"

        return Response({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "total_products": total_products,
            "active_products": active_products,
            "outofstock": outofstock,
            "lowstock": lowstock,
            "inactive":inactive,
            "next": build_url(page_obj.next_page_number()) if page_obj.has_next() else None,
            "previous": build_url(page_obj.previous_page_number()) if page_obj.has_previous() else None,
            "results": serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        brand_input = request.data.get("brand")
        product_name = request.data.get("name")

        if not brand_input:
            return Response({"error": "Brand information is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle brand
        if isinstance(brand_input, int) or str(brand_input).isdigit():
            brand = get_object_or_404(Brand, id=brand_input)
        elif isinstance(brand_input, dict) and brand_input.get("name"):
            brand_name = brand_input["name"].strip()
            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={"description": brand_input.get("description", "")},
            )
        else:
            return Response({"error": "Invalid brand format."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate product
        if Product.objects.filter(brand=brand, name__iexact=product_name).exists():
            return Response(
                {"warning": f"Product '{product_name}' already exists under brand '{brand.name}'."},
                status=status.HTTP_409_CONFLICT
            )

        # Save product
        product_data = request.data.copy()
        product_data["brand"] = brand.id
        image_urls = product_data.pop("images", [])  # Remove images before serializer
        serializer = AdminProductSerializer(data=product_data)
        if serializer.is_valid():
            product = serializer.save(brand=brand)

            # Save images
            if isinstance(image_urls, list):
                for url in image_urls:
                    ProductImage.objects.create(product=product, image_url=url)

            return Response(AdminProductSerializer(product).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        brand_input = request.data.get("brand")

        # Handle brand update
        if brand_input:
            if isinstance(brand_input, int) or str(brand_input).isdigit():
                brand = get_object_or_404(Brand, id=brand_input)
            elif isinstance(brand_input, dict) and brand_input.get("name"):
                brand_name = brand_input["name"].strip()
                brand, _ = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={"description": brand_input.get("description", "")},
                )
            else:
                return Response({"error": "Invalid brand format."}, status=status.HTTP_400_BAD_REQUEST)
            request.data["brand"] = brand.id
        else:
            brand = product.brand

        # Handle images: pop to prevent serializer issues
        image_urls = request.data.pop("images", None)

        serializer = AdminProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save(brand=brand)

            # Only replace images if new ones are provided
            if image_urls is not None and isinstance(image_urls, list):
                ProductImage.objects.filter(product=product).delete()
                for url in image_urls:
                    ProductImage.objects.create(product=product, image_url=url)

            return Response(AdminProductSerializer(updated_product).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)