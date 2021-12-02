import abc
import requests
from collections import OrderedDict

from django.shortcuts import HttpResponse

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from elasticsearch_dsl import Q

from .models import (
    Category, Product
)
from .serializers import (
    CategorySerializer,
    ProductSerializer
)
from .documents import CategoryDocument, ProductDocument


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


class ListProducts(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
     


class ElasticSearchAPIView(APIView):
    serializer_class = None
    document_class = None

    @abc.abstractmethod
    def generate_q_expression(self, query):
        "The method must be overridden to return query expression"
        pass

    def get(self, request, query):
        try:
            q = self.generate_q_expression(query)
            search = self.document_class.search().query(q)
            response = search.execute()

            print(f'Found {response.hits.total.value} hit(s) for query: "{query}"')

            serializer = self.serializer_class(response, many=True)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return HttpResponse(e, status=500)


class SearchProducts(ElasticSearchAPIView):
    serializer_class = ProductSerializer
    document_class = ProductDocument

    def generate_q_expression(self, query):
        return Q('bool',
                 should=[
                     Q('match', title=query),
                     Q('match', category__title=query),
                 ])


class SearchCategories(ElasticSearchAPIView):
    serializer_class = CategorySerializer
    document_class = CategoryDocument

    def generate_q_expression(self, query):
        return Q(
            "bool",
            should=[
                Q("match", title=query),
            ]
        )
