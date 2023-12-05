# celery.py
import os
from celery import Celery

# postavite defaultne Django postavke za Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('timee')

# Učitajte postavke iz vašeg Django settings fajla
app.config_from_object('django.conf:settings', namespace='CELERY')

# Otkrijte zadatke iz svih registrovanih Django app aplikacija
app.autodiscover_tasks()
