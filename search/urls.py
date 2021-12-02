from django.urls import path

from .views import (
    SearchProducts, SearchCategories, FilterProducts
)

urlpatterns = [
    path(
        'search-products/<str:query>/',
        SearchProducts.as_view(),
        name='search-products'
    ),
    path(
        'search-categories/<str:query>/',
        SearchCategories.as_view(),
        name='search-categories'
    ),
    path(
        'filter-products/',
        FilterProducts.as_view(),
        name='filter-products'
    ),
]