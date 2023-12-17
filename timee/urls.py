from django.urls import path
from . import views

app_name = "timee"

urlpatterns = [
    path('', views.index, name="homepage"),
    path('sport/', views.sport, name="sport"),
    path('magazin/', views.magazin, name="magazin"),
    path('bih/', views.bih_category, name='bih_category'),
    path('ekonomija/', views.ekonomija_category, name="ekonomija"),
    path('balkan/', views.balkan_category, name="balkan_category"),
    path('svijet/', views.svijet_category, name="svijet_category"),
    path('sarajevo/', views.sarajevo_category, name="sarajevo_category"),
    path('hronika/', views.hronika_category, name="hronika_category"),
    path('kultura/',views.kultura_category, name="kultura_category"),
    path('scena/', views.scena_category, name="scena_category"),
    path('sport/fudbal/', views.fudbal_category, name="fudbal_category"),
    path('sport/kosarka/', views.kosarka_category, name="kosarka_category"),
    path('sport/tenis', views.tenis_category, name="tenis_category"),
    path('sport/ostalo', views.ostalo_category, name="ostalo_category"),
    path('magazin/zabava', views.zabava_category, name="zabava_category"),
    path('magazin/automobili', views.automobili_category, name="automobili_category"),
    path('magazin/tehnologija', views.tehnologija_category, name="tehnologija_category"),
    path('magazin/lifestyle', views.lifestyle_category, name="lifestyle_category"),
    path('magazin/hrana', views.hrana_category, name="hrana_category"),
    path('magazin/intima', views.intima_category, name="intima_category"),
    path('najnovije_vijesti/',views.najnovije_vijesti, name="najnovije_vijesti"),
    path('izvori/', views.izvori, name="izvori"),
    path('info/contact/', views.contact, name='contact'),
    path('info/week/', views.news_archive, name='week'),
    path('info/prognoza/', views.prognoza, name='prognoza'),
    path('news-archive/', views.news_archive, name='news_archive'),
    path('widget/widgetpage', views.widget, name='widget'),
    path('rss/rsspage', views.rsspage, name='rsspage'),
    path('m/', views.mobile, name='mobile_index'),
    path('firme/', views.company_directory, name='firme'),
    path('opstine/<str:city_name>/', views.city_companies, name='city_companies'),
    path('pretraga/', views.search_news, name='search_news'),
    path('10h/', views.news_at_10, name="10h"),
    path('17h/', views.news_last_17_hours, name="17h"),
    path('c/<int:pk>/related/', views.related_news_view, name='related_news'),


    
   
 

]