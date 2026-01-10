import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evoting_system.settings')

app = Celery('evoting_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
