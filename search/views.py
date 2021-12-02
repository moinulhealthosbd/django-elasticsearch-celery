import abc

from django.shortcuts import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from elasticsearch_dsl import Q

from core.serializers import (
    CategorySerializer, ProductSerializer
)
from .documents import (
    CategoryDocument, ProductDocument
)


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
            serializer = self.serializer_class(response, many=True)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return HttpResponse(e, status=500)


class SearchProducts(ElasticSearchAPIView):
    """Search products by a query that will match with product title or category"""

    serializer_class = ProductSerializer
    document_class = ProductDocument

    def generate_q_expression(self, query):
        return Q('bool',
                 should=[
                     Q('match', title=query),
                     Q('match', category__title=query),
                 ])


class SearchCategories(ElasticSearchAPIView):
    """Searches category by a query that will match with the category title"""

    serializer_class = CategorySerializer
    document_class = CategoryDocument

    def generate_q_expression(self, query):
        return Q(
            "bool",
            should=[
                Q("match", title=query),
            ]
        )


class FilterProducts(APIView):
    """
    Filtered products by the provided category title (exact)
    plus provided price that is lte product price
    """
    serializer_class = ProductSerializer
    document_class = ProductDocument

    def get(self, *args, **kwargs):
        category = self.request.GET.get("category", None)
        price = self.request.GET.get("price", None)
        search = self.document_class.search()

        if category:
            search = search.filter("match", category__title=category)

        if price:
            search = search.filter(
                "range",
                price={"lte": price}
            )

        response = search.execute()
        serializer = self.serializer_class(response, many=True)
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )