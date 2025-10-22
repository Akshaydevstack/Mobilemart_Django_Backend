from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from .models import ProductReview, Product
from .serializers import ProductReviewSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('brand').prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

      # --- Add filtering, search, ordering ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering by these fields
    filterset_fields = {
        'brand__id': ['exact'],     # filter by brand id
        'is_active': ['exact'],     # active products
        'price': ['gte', 'lte'],    # price range
    }
    
    # Search in name, description, brand name
    search_fields = ['name', 'description', 'brand__name']
    
    # Ordering options
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['id']  # default ordering

    def create(self, request, *args, **kwargs):
        # Check if the request contains a list of products
        is_many = isinstance(request.data, list)
        
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
  
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