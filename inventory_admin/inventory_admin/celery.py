import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_admin.settings')

app = Celery('inventory_admin')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
app = Celery('inventory_admin')
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/1'
from celery import Celery

app = Celery('inventory_admin')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
