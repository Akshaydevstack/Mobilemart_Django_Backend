from rest_framework import viewsets, permissions
from .models import Brand
from .serializers import BrandSerializer
from rest_framework.views import APIView

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]


