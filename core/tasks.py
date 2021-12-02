import random
from decimal import Decimal
from datetime import time, timedelta

from celery import shared_task
from celery.decorators import periodic_task

from .models import Product


# This will update every product price randomly
@shared_task
def update_product_price():
    products = Product.objects.all()

    for product in products:
        product.price = Decimal(float(random.randrange(100, 500)))
        product.save()

    print("---------updating product price --------")


@shared_task
def greet(user):
    print(f"--------Hi, {user}--------, ")


@periodic_task(run_every=timedelta(seconds=60))
def update():
    update_product_price.delay()


@periodic_task(run_every=timedelta(seconds=20))
def greet_user():
    greet.delay("nabil")
