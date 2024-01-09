from django.urls import path
from . import views
from . import izvori

app_name = "timee"

urlpatterns = [
    path('', views.index, name="homepage"),
    path('st/sport/', views.sport, name="sport"),
    path('st/magazin/', views.magazin, name="magazin"),
    path('st/vijesti/bih/', views.bih_category, name='bih_category'),
    path('st/vijesti/ekonomija/', views.ekonomija_category, name="ekonomija"),
    path('st/vijesti/balkan/', views.balkan_category, name="balkan_category"),
    path('st/vijesti/svijet/', views.svijet_category, name="svijet_category"),
    path('st/vijesti/sarajevo/', views.sarajevo_category, name="sarajevo_category"),
    path('st/vijesti/hronika/', views.hronika_category, name="hronika_category"),
    path('st/vijesti/kultura/',views.kultura_category, name="kultura_category"),
    path('st/vijesti/scena/', views.scena_category, name="scena_category"),
    path('st/sport/fudbal', views.fudbal_category, name="fudbal_category"),
    path('st/sport/kosarka', views.kosarka_category, name="kosarka_category"),
    path('st/sport/tenis', views.tenis_category, name="tenis_category"),
    path('st/sport/ostalo', views.ostalo_category, name="ostalo_category"),
    path('st/magazin/zabava', views.zabava_category, name="zabava_category"),
    path('st/magazin/automobili', views.automobili_category, name="automobili_category"),
    path('st/magazin/tehnologija', views.tehnologija_category, name="tehnologija_category"),
    path('st/magazin/lifestyle', views.lifestyle_category, name="lifestyle_category"),
    path('st/magazin/hrana', views.hrana_category, name="hrana_category"),
    path('st/magazin/intima', views.intima_category, name="intima_category"),
    path('n/najnovije_vijesti/',views.najnovije_vijesti, name="najnovije_vijesti"),
    path('s/izvori/', views.izvori, name="izvori"),
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
    path('c/<int:pk>/related/', views.related_news_view, name='related_news'),
    #rute vezane za izvore samo 
    path('s/svi', izvori.svi_izvori, name='svi_izvori'), 
    path('s/<str:kljucna_rijec>/', izvori.prikaz_izvora, name='prikaz_izvora'),    
     


    
   
 

]