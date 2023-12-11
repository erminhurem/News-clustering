import feedparser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from dateutil import parser as date_parser
from django.utils.timezone import make_aware, now
from .models import Headlines
from bs4 import BeautifulSoup
import logging
from django.db.models import Count
import datetime
import requests

# Pomoćna funkcija za pretvaranje URL-a izvora u prijateljsko ime
def get_friendly_source_name(url):
    if 'telegraf.rs' in url:
        return 'Telegraf'
    elif 'kurir.rs' in url:
        return 'Kurir'
    elif 'www.euronews.rs' in url:
        return 'Euronews'
    elif 'nova.rs' in url:
        return 'Nova'
    elif 'n1info.ba' in url:
        return 'N1'
    elif 'klix.ba' in url:
        return 'Klix'
    elif 'balkans.aljazeera.net' in url:
        return 'Aljazeera'
    elif 'avaz.ba' in url:
        return 'Dnevni avaz'
    elif 'vijesti.ba' in url:
        return 'Vijesti'
    elif 'okanal.oslobodjenje.ba/okanal' in url:
        return 'Okanal'
    else:
        return 'Nepoznati izvor'
    
# Pomoćna funkcija za dobijanje relativnog vremena
def get_relative_time(published_date):
    if published_date:
        delta = now() - published_date
        if delta.days > 0:
            return f"prije {delta.days} dana"
        elif delta.seconds // 3600 > 0:
            return f"prije {delta.seconds // 3600} sati"
        elif delta.seconds // 60 > 0:
            return f"prije {delta.seconds // 60} minuta"
        else:
            return "upravo objavljeno"
    return "Nepoznato vrijeme"

# početak koda vezano za rubriku Vijesti
def index(request):
    latest_news = Headlines.objects.all().order_by('-published_date')[:3]
    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    categories = ['Ekonomija', 'BiH', 'Balkan', 'Svijet', 'Hronika', 'Sarajevo', 'Kultura', 'Scena', 'Sport', 'Magazin']
    news_by_category = {}
    for category in categories:
        news_items = Headlines.objects.filter(category=category).order_by('-published_date')[:3]
        for item in news_items:
            item.source_name = get_friendly_source_name(item.source)
            item.time_since = get_relative_time(item.published_date)
        news_by_category[category] = news_items

    context = {
        'latest_news': latest_news,
        'news_by_category': news_by_category,
    }
    return render(request, "index.html", context)

def bih_category(request):
    news_items = Headlines.objects.filter(category='BiH').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'BiH': news_page},
        'latest_news': news_page.object_list,
    }
    return render(request, "bih_category.html", context)

def ekonomija_category(request):
    news_items = Headlines.objects.filter(category='Ekonomija').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Ekonomija': news_page},
        'latest_news': news_page.object_list,
    }
    return render(request, "ekonomija_category.html", context)

def balkan_category(request):
    news_items = Headlines.objects.filter(category='Balkan').order_by('-published_date')

    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
       
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Balkan': news_page},
         'naslov_stranice': 'Balkan - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "balkan_category.html", context)

def svijet_category(request):
    news_items = Headlines.objects.filter(category='Svijet').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
       
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Svijet': news_page},
         'naslov_stranice': 'Svijet - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "svijet_category.html", context)

def sarajevo_category(request):
    news_items = Headlines.objects.filter(category='Sarajevo').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Sarajevo': news_page},
        'naslov_stranice': 'Sarajevo - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "sarajevo_category.html", context)

def hronika_category(request):
    news_items = Headlines.objects.filter(category='Hronika').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Hronika': news_page},
          'naslov_stranice': 'Hronika - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "hronika_category.html", context)

def kultura_category(request):
    news_items = Headlines.objects.filter(category='Kultura').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Kultura': news_page},
        'naslov_stranice': 'Kultura - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "kultura_category.html", context)

def scena_category(request):
    news_items = Headlines.objects.filter(category='Scena').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Scena': news_page},
        'naslov_stranice': 'Scena - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "scena_category.html", context)

# kraj koda vezano za rubriku Vijesti

# početak koda vezano za rubriku Sport
def sport(request):
    latest_news = Headlines.objects.filter(category="Sport").order_by('-published_date')[:3]
    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    categories = ['Fudbal', 'Kosarka', 'Tenis', 'Ostalo', 'Vijesti', 'Magazin']
    news_by_category = {}
    for category in categories:
        news_items = Headlines.objects.filter(category=category).order_by('-published_date')[:3]
        for item in news_items:
            item.source_name = get_friendly_source_name(item.source)
            item.time_since = get_relative_time(item.published_date)
        news_by_category[category] = news_items

    context = {
        'latest_news': latest_news,
        'naslov_stranice': 'Sport - Time.ba',
        'news_by_category': news_by_category,
    }
    return render(request, "sport.html", context)

def fudbal_category(request):
    news_items = Headlines.objects.filter(category='Fudbal').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Fudbal': news_page},
        'naslov_stranice': 'Fudbal - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "fudbal_category.html", context)

def kosarka_category(request):
    news_items = Headlines.objects.filter(category='Kosarka').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Kosarka': news_page},
        'naslov_stranice': 'Kosaraka - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "kosarka_category.html", context)

def tenis_category(request):
    news_items = Headlines.objects.filter(category='Tenis').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Tenis': news_page},
        'naslov_stranice': 'Tenis - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "tenis_category.html", context)

def ostalo_category(request):
    news_items = Headlines.objects.filter(category='Ostalo').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Ostalo': news_page},
        'naslov_stranice': 'Ostalo - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "ostalo_category.html", context)

# kraj koda vezano za rubriku Sport

# početak koda vezano za rubriku Magazin

def magazin(request):
    latest_news = Headlines.objects.filter(category="Magazin").order_by('-published_date')[:3]
    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    categories = ['Zabava', 'Automobili / Motori', 'Tehnologija', 'Lifestyle','Hrana / Zdravlje','Intima / Sex', 'VIJESTI','SPORT']
    news_by_category = {}
    for category in categories:
        news_items = Headlines.objects.filter(category=category).order_by('-published_date')[:3]
        for item in news_items:
            item.source_name = get_friendly_source_name(item.source)
            item.time_since = get_relative_time(item.published_date)
        news_by_category[category] = news_items

    context = {
        'latest_news': latest_news,
         'naslov_stranice': 'Magazin - Time.ba',
        'news_by_category': news_by_category,
    }
    return render(request, "magazin.html", context)

def zabava_category(request):
    news_items = Headlines.objects.filter(category='Zabava').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Zabava': news_page},
         'naslov_stranice': 'Zabava - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "zabava_category.html", context)

def automobili_category(request):
    news_items = Headlines.objects.filter(category='Automobili / Motori').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Automobili': news_page},
        'naslov_stranice': 'Automobili - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "automobili_category.html", context)

def tehnologija_category(request):
    news_items = Headlines.objects.filter(category='Tehnologija').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        news_page = paginator.page(1)
    except EmptyPage:
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Dodajte ovdje informacije o aktivnoj glavnoj kategoriji i podkategoriji
    context = {
        'news_by_category': {'Tehnologija': news_page},
        'latest_news': news_page.object_list,
        'naslov_stranice': 'Tehnologija - Time.ba',
         'aktivna_kategorija': 'Magazin',
        'aktivna_podkategorija': 'Tehnologija',
    }

    return render(request, "tehnologija_category.html", context)


def lifestyle_category(request):
    news_items = Headlines.objects.filter(category='Lifestyle').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Lifestyle': news_page},
         'naslov_stranice': 'Lifestyle - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "lifestyle_category.html", context)

def hrana_category(request):
    news_items = Headlines.objects.filter(category='Hrana / Zdravlje').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Hrana': news_page},
        'naslov_stranice': 'Hrana - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "hrana_category.html", context)

def intima_category(request):
    news_items = Headlines.objects.filter(category='Intima / Sex').order_by('-published_date')
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)

    for news in news_page:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'news_by_category': {'Intima': news_page},
         'naslov_stranice': 'Intima - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "intima_category.html", context)

# kraj koda vezano za rubriku Magazin

def najnovije_vijesti(request):
    latest_news = Headlines.objects.all().order_by('-published_date')[:3]
    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    context = {
        'latest_news': latest_news,
         'naslov_stranice': 'Vijesti - Time.ba',
    }

    return render(request, "najnovije_vijesti.html", context)

def izvori(request):

    return render(request, "izvori.html")

def film(request):

    return render(request, "film.html")


def fetch_news():
    feeds = [
        'https://www.telegraf.rs/rss',
        'https://www.kurir.rs/rss',
        'https://nova.rs/rss',
        'https://n1info.ba/feed/',
        'https://www.euronews.rs/rss',
        'https://informer.rs/rss',
        'https://n1info.ba/rss',
        'https://n1info.hr/rss',
        'https://www.vijesti.ba/rss/svevijesti',
        'https://balkans.aljazeera.net/rss.xml',
        'https://www.klix.ba/rss',
        'https://www.avaz.ba/rss',
        'https://www.oslobodjenje.ba/feed',
        'https://okanal.oslobodjenje.ba/okanal/feed',
    ]
    logger = logging.getLogger(__name__)
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if not Headlines.objects.filter(link=entry.link).exists():
                published_date = None
                if entry.published:
                    try:
                        published_date = date_parser.parse(entry.published)
                    except ValueError:
                        pass

                content = entry.content[0].value if 'content' in entry else ''
                soup = BeautifulSoup(content, 'html.parser')
                images = soup.find_all('img')

                image_urls = [img['src'] for img in images]

                category = categorize_news(entry.link)  # Ovdje dodajemo kategoriju

                news_item = Headlines(
                    title=entry.title,
                    link=entry.link,
                    description=entry.description,
                    published_date=published_date,
                    source=feed_url,
                    category=category,  # Dodajemo kategoriju u model
                    image_urls=','.join(image_urls) if image_urls else None
                )
                logger.info('Fetching news from %s', feed_url)
                news_item.save()

def categorize_news(url):
    if 'ekonomija' in url or 'biznis' in url or 'economy' in url:
        return 'Ekonomija'
    elif 'sport' in url:
        return 'Sport'
    elif 'bih' in url or 'bosna-i-hercegovina' in url:
        return 'BiH'
    elif 'balkan' in url or 'region' in url:
        return 'Balkan'
    elif 'sarajevo' in url:
        return 'Sarajevo'
    elif 'svijet' in url or 'svet' in url:
        return 'Svijet'
    elif 'hronika' in url or 'crna-hronika' in url:
        return 'Hronika'
    elif 'politika' in url:
        return 'Politika'
    elif 'kultura' in url:
        return 'Kultura'
    elif 'zabava' in url:
        return 'Zabava'
    elif 'lifestyle' in url:
        return 'Lifestyle'
    elif 'hrana' or 'zdravlje'in url:
        return 'Hrana / Zdravlje'
    elif 'tehnologija' in url:
        return 'Tehnologija'
    elif 'intima' or 'sex' in url:
        return 'Intima / Sex'
    elif 'zdravlje' in url:
        return 'Zdravlje'
    elif 'magazin' in url:
        return 'Magazin'
    elif 'scena' or 'showbiz' in url:
        return 'Scena'
    elif 'fudbal' or 'nogomet' in url:
        return 'Fudbal'
    elif 'košarka' or 'kosarka' or 'sport/kosarka' or 'sport-klub/kosarka' in url:
        return 'Kosarka'
    elif 'tenis' in url:
        return 'Tenis'
    elif 'plivanje' or 'rukomet' or 'atletika' in url:
        return 'Ostalo'
    elif 'automobili' or 'motori' in url:
        return 'Automobili / Motori'
    else:
        return 'Vijesti'


def contact(request):
    return render(request, 'kontakt.html')



def news_archive(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from and date_to:
        news_items = Headlines.objects.filter(published_date__range=[date_from, date_to])
    else:
        news_items = Headlines.objects.all()

    paginator = Paginator(news_items, 10)  # 10 vijesti po stranici
    page = request.GET.get('page')

    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)

    return render(request, 'week.html', {'news': news})
