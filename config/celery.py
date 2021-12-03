import os
from datetime import time, timedelta

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_shedule = {
    "update_product_3s": {
        "task": "core.tasks.update",
    },
    "greet_user": {
        "task": "core.tasks.greet_user"
    },
}

app.autodiscover_tasks()