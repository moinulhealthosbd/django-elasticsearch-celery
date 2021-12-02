from django.urls import path

from .views import CreateProducts, ListProducts, SearchCategories, SearchProducts


urlpatterns = [
    path(
        'create-products/',
        CreateProducts.as_view(),
        name='create-products'
    ),
    path(
        'list-products/',
        ListProducts.as_view(),
        name='list-products'
    ),
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

]