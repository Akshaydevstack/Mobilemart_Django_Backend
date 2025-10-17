from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Brand
from .serializers import BrandSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]