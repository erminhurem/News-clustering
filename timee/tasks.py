
from celery import shared_task
from .views import fetch_news  

@shared_task
def task_fetch_news():
    fetch_news()
