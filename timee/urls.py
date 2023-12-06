from django.urls import path
from . import views

app_name = "timee"

urlpatterns = [
    path('', views.index, name="homepage"),
    path('sport/', views.sport, name="sport"),
    path('magazin/', views.magazin, name="magazin"),
]