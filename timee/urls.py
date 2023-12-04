from django.urls import path
from . import views

app_name = "timee"

urlpatterns = [
    path('', views.index, name="homepage")
]