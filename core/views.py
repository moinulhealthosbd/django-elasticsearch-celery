import requests
from collections import OrderedDict 

from django.shortcuts import HttpResponse

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination

from elasticsearch_dsl import Q

from .models import (
    Category, Product
)
from .serializers import (
    ProductSerializer
)
from .documents import ProductDocument


class CreateProducts(APIView):
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


class ElasticSearchAPIView(APIView):
    serializer_class = None
    document_class = None

    def generate_q_expression(self, query):
        pass

    def get(self, request, query):
        try:
            q = self.generate_q_expression(query)
            search = self.document_class.search().query(q)
            response = search.execute()
            results = []

            for result in response:
                product = Product.objects.get(id=result.id)
                serializer = ProductSerializer(product)
                results.append(serializer.data)

            return Response(
                results,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return HttpResponse(e, 500)


class SearchProducts(ElasticSearchAPIView):
    serializer_class = ProductSerializer
    document_class = ProductDocument

    def generate_q_expression(self, query):
        return Q('bool',
                 should=[
                     Q('match', title=query),
                 ], minimum_should_match=1)


class ListProducts(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
     


# class PaginatedElasticSearchAPIView(APIView, LimitOffsetPagination):
#     serializer_class = None
#     document_class = None

#     def generate_q_expression(self, query):
#         pass

#     def get_paginated_response(self, data):
#         return Response(OrderedDict([
#             ('results', data)
#         ]))

#     def get(self, request, query):
#         try:
#             q = self.generate_q_expression(query)
#             search = self.document_class.search().query(q)
#             response = search.execute()

#             print(f'Found {response.hits.total.value} hit(s) for query: "{query}"')

#             results = self.paginate_queryset(response, request, view=self)
#             print("data----")
#             serializer = self.serializer_class(results, many=True)
#             print("success---", serializer.data)
#             return self.get_paginated_response(serializer.data)
#         except Exception as e:
#             return HttpResponse(e, status=500)


# class SearchProducts(PaginatedElasticSearchAPIView, LimitOffsetPagination):
#     serializer_class = ProductSerializer
#     document_class = ProductDocument

#     def generate_q_expression(self, query):
#         return Q('bool',
#                  should=[
#                      Q('match', title=query),
#                  ], minimum_should_match=1)
    