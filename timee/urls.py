from django.urls import path
from . import views

app_name = "timee"

urlpatterns = [
    path('', views.index, name="homepage"),
    path('sport/', views.sport, name="sport"),
    path('magazin/', views.magazin, name="magazin"),
    path('bih/', views.bih_category, name='bih_category'),
    path('ekonomija/', views.ekonomija_category, name="ekonomija_category"),
    path('balkan/', views.balkan_category, name="balkan_category"),
    path('svijet/', views.svijet_category, name="svijet_category"),
    path('sarajevo/', views.sarajevo_category, name="sarajevo_category"),
    path('hronika/', views.hronika_category, name="hronika_category"),
    path('kultura/',views.kultura_category, name="kultura_category"),
    path('scena/', views.scena_category, name="scena_category"),
    path('fudbal/', views.fudbal_category, name="fudbal_category"),
    
]