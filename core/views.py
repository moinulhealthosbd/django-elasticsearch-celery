import requests

from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


from .models import (
    Category, Product
)
from .serializers import (
    ProductSerializer
)


class CreateProducts(APIView):
    """Creates some products data from an external api"""
    
    def get(self, *args, **kwargs):
        url = "https://fakestoreapi.com/products"
        response = requests.get(url).json()

        for product in response:
            category, created = Category.objects.get_or_create(
                title=product['category']
            )
            Product.objects.create(
                category=category,
                title=product['title'],
                price=product['price'],
                description=product['description'],
                image_url=product['image']
            )

        queryset = Product.objects.all()
        serializer = ProductSerializer(queryset, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CacheApiView(APIView):
    model = None
    serializer_class = None
    cache_key = None

    def get(self, *args, **kwargs):
        queryset = cache.get(self.cache_key)
        print(queryset)

        if queryset:
            serializer = self.serializer_class(queryset, many=True)
        else:
            queryset = self.model.objects.all()
            cache.set(
                self.cache_key,
                queryset,
                None
            )
            serializer = self.serializer_class(queryset, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ListProducts(CacheApiView):
    model = Product
    serializer_class = ProductSerializer
    cache_key = "products"
