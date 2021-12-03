from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Product

from .tasks import update_product_cache


@receiver(post_save, sender=Product)
def update_product_cache_after_adding_or_updating__product(instance, created, *args, **kwargs):
    update_product_cache.delay()
    cache.set("products", Product.objects.all())
