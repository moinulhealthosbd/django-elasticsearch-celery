import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Product
from .serializers import ProductSerializer



@receiver(post_save, sender=Product)
def update_product_cache_after_adding_or_updating__product(instance, created, *args, **kwargs):
    product_id = instance.id
    products = cache.get("products")
    new_product = ProductSerializer(instance)

    if products:
        products.update({str(product_id): new_product.data})
        cache.set("products", products)
    else:
        cache.set("products", {str(product_id): new_product.data})
