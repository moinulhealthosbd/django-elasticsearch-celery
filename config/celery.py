import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_shedule = {
    "update_product_3s": {
        "task": "core.tasks.update_product_price",
        "schedule": 3.0
    }
}

app.autodiscover_tasks()