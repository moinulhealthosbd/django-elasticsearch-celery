import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Product


@receiver(post_save, sender=Product)
def update_cache_after_adding_or_updating__product(instance, created, *args, **kwargs):
    products = cache.get("products")

    if products:
        cache.delete("products")