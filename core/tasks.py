import random
from decimal import Decimal

from celery import shared_task

from .models import Product

@shared_task
def update_product_price():
    products = Product.objects.all()

    for product in products:
        product.price = Decimal(float(random.randrange(100, 500)))
        product.save()

    print("updating product price")