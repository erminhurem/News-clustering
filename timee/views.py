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
from django.http import JsonResponse
import datetime
import requests
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from dateutil import parser
from .company_directory import create_company_directory_adjusted
from django.conf import settings
import pandas as pd





nltk.download('punkt')


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
    elif 'n1info.hr' in url:
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
    elif 'oslobodjenje.ba' in url:
        return 'Oslobođenje'
    elif 'alo.rs' in url:
        return 'Alo'
    elif '24sata.hr' in url:
        return '24sata'
    elif 'vecernji.hr' in url:
        return 'Vecernji'
    elif 'sd.rs' in url:
        return 'SD'
    elif 'blic.rs' in url:
        return 'Blic'
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


def extract_keywords(text):
    words = nltk.word_tokenize(text)
    keywords = [word for word in words if word.isalnum()]
    return keywords

# početak koda vezano za rubriku Vijesti
def index(request):
    latest_news = Headlines.objects.all().order_by('-published_date')[:3]
    all_news = Headlines.objects.all().order_by('-published_date')
    vectorizer = TfidfVectorizer()
    
    # Koristimo 'description' polje za izračunavanje TF-IDF vektora
    tfidf_matrix = vectorizer.fit_transform([' '.join(extract_keywords(news.description)) for news in all_news])

    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

        # Izračunavanje TF-IDF vektora za trenutnu vijest
        current_tfidf = vectorizer.transform([' '.join(extract_keywords(news.description))])
        cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

        # Dobivanje indeksa povezanih članaka
        related_articles_indices = cosine_similarities[0].argsort()[:-6:-1]

        # Preuzmite povezane vijesti i izračunajte njihov ukupan broj
        related_news = [all_news[i.item()] for i in related_articles_indices if all_news[i.item()].id != news.id][:5]
        news.related_news = related_news
        # Ovdje postavite ukupan broj povezanih vijesti
        news.related_news_count = len(related_news)
        for news in related_news:
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
        'naslov_stranice': 'Vijesti - Time.ba',
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
        'naslov_stranice': 'BiH - Time.ba',
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
        'naslov_stranice': 'Ekonomija - Time.ba',
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
    latest_news_s = Headlines.objects.filter(category="Sport").order_by('-published_date')[:3]    
    for news_s in latest_news_s:
        news_s.source_name = get_friendly_source_name(news_s.source)
        news_s.time_since = get_relative_time(news_s.published_date)

    latest_news = Headlines.objects.all().order_by('-published_date')[:3]
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
        'latest_news_s': latest_news_s,
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
    latest_news_m = Headlines.objects.filter(category="Magazin").order_by('-published_date')[:3]
    for news_m in latest_news_m:
        news_m.source_name = get_friendly_source_name(news_m.source)
        news_m.time_since = get_relative_time(news_m.published_date)

    latest_news = Headlines.objects.all().order_by("-published_date")[:3]
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
        'latest_news_m': latest_news_m,
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
    news_items = Headlines.objects.filter(category='Automobili').order_by('-published_date')
    
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
    kategorije = [
        'Ekonomija', 'Sport', 'BiH', 'Balkan', 'Sarajevo',
        'Svijet', 'Hronika', 'Politika', 'Kultura', 'Zabava',
        'Lifestyle', 'Hrana / Zdravlje', 'Tehnologija',
        'Intima / Sex', 'Zdravlje', 'Magazin', 'Scena',
        'Fudbal', 'Košarka', 'Tenis', 'Ostalo', 'Automobili / Motori', 'Vijesti'
    ]
    topic = request.GET.get('topic', 'all')  # 'all' je default vrijednost
    if topic not in kategorije:
        topic = 'all'

    if topic == 'all':
        latest_news = Headlines.objects.all().order_by('-published_date')[:10]
    else:
        latest_news = Headlines.objects.filter(category=topic).order_by('-published_date')[:10]
    
    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)
    # Paginacija
    page = request.GET.get('page', 1)
    paginator = Paginator(latest_news, 10) 
    try:
        latest_news = paginator.page(page)
    except PageNotAnInteger:
        latest_news = paginator.page(1)
    except EmptyPage:
        latest_news = paginator.page(paginator.num_pages)

    context = {
        'latest_news': latest_news,
        'naslov_stranice': 'Vijesti - Time.ba',
        'selected_topic': topic,
        'kategorije': kategorije,
    }

    return render(request, "najnovije_vijesti.html", context)


def izvori(request):

    return render(request, "izvori.html")

def firme(request):
    context = {'naslov_stranice': 'Firme - Time.ba',}
    return render(request, "firme.html", context)


def extract_images(entry):
    images = []

     # Ekstrakcija iz 'media:content' ako postoji
    if 'media_content' in entry:
        media_content = entry.media_content
        if media_content:
            images.extend([content['url'] for content in media_content if 'url' in content])

    # Dodatna ekstrakcija iz 'content' ako postoji
    if 'content' in entry:
        content = entry.content[0].value
        soup = BeautifulSoup(content, 'html.parser')
        images.extend([img['src'] for img in soup.find_all('img')])

    # Ekstrakcija iz 'image' ako postoji
    if 'image' in entry:
        image = entry.image
        if image and 'url' in image:
            images.append(image['url'])

     # Ekstrakcija iz 'enclosure' ako postoji
    if 'enclosures' in entry:
        enclosures = entry.enclosures
        images.extend([enclosure['url'] for enclosure in enclosures if 'url' in enclosure])

    # Ekstrakcija iz 'description' ako sadrži 'img' tagove
    if 'description' in entry:
        description = entry.description
        soup = BeautifulSoup(description, 'html.parser')
        images.extend([img['src'] for img in soup.find_all('img')])

    # Ekstrakcija direktnog URL-a iz 'image' ako postoji
    if 'image' in entry:
        image = entry.image
        if isinstance(image, str):
            images.append(image)
        elif image and 'url' in image:
            images.append(image['url'])

     # Ekstrakcija iz 'icon' ako postoji
    if 'icon' in entry:
        icon = entry.icon
        if isinstance(icon, str):
            images.append(icon)
        elif icon and 'url' in icon:
            images.append(icon['url'])

    return images


def parse_date(date_str):
    try:
        return parser.parse(date_str)
    except ValueError as e:
        logger.error(f"Greška prilikom parsiranja datuma: {e}")
        return None


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
        'https://www.b92.net/feed/',
        'https://www.sd.rs/rss.xml',
        'https://www.rts.rs/rss/ci.html',
        'https://www.alo.rs/rss/live',
        'https://www.alo.rs/rss/hronika',
        'https://www.alo.rs/rss/biz',
        'https://www.alo.rs/rss/vesti',
        'https://www.espreso.co.rs/rss',
        'https://www.vecernji.hr/feeds/latest',
        'https://dnevnik.hr/assets/feed/articles',
        'https://www.24sata.hr/feeds/najnovije.xml',
        'https://www.24sata.hr/feeds/news.xml',
        'https://www.24sata.hr/feeds/sport.xml',
        'https://www.24sata.hr/feeds/tech.xml',

    ]
    logger = logging.getLogger(__name__)
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if not Headlines.objects.filter(link=entry.link).exists():
                published_date = parse_date(entry.published) if entry.published else None

                image_urls = extract_images(entry)  # Koristi definisanu funkciju za ekstrakciju slika

                category = categorize_news(entry.link)  # Ovdje dodajemo kategoriju

                news_item = Headlines(
                    title=entry.title,
                    link=entry.link,
                    description=entry.description,
                    published_date=published_date,
                    source=feed_url,
                    category=category, 
                    image_urls=','.join(image_urls) if image_urls else None
                )
                logger.info('Fetching news from %s', feed_url)
                news_item.save()
        

def categorize_news(url):
    # Mapiranje ključnih riječi na kategorije
    kategorije = {
        'Ekonomija': ['ekonomija', 'biznis', 'economy'],
        'Fudbal': ['fudbal', 'nogomet'],
        'Košarka': ['košarka', 'kosarka', 'sport/kosarka', 'sport-klub/kosarka'],
        'Tenis': ['tenis'],
        'Ostalo': ['plivanje', 'rukomet', 'atletika', 'skijanje'],
        'Automobili': ['automobili', 'motori'],
        'BiH': ['bih', 'bosna-i-hercegovina'],
        'Balkan': ['balkan', 'region'],
        'Sarajevo': ['sarajevo'],
        'Svijet': ['svijet', 'svet'],
        'Hronika': ['hronika', 'crna-hronika'],
        'Politika': ['politika'],
        'Kultura': ['kultura'],
        'Zabava': ['zabava'],
        'Lifestyle': ['lifestyle'],
        'Hrana': ['hrana', 'zdravlje'],
        'Tehnologija': ['tehnologija'],
        'Intima': ['intima', 'sex'],
        'Zdravlje': ['zdravlje'],
        'Magazin': ['magazin'],
        'Scena': ['scena', 'showbiz'],
        'Vijesti': ['vijesti', 'vesti']
    }

    # Provjera svake kategorije
    for kategorija, kljucne_rijeci in kategorije.items():
        if any(kljucna_rijec in url for kljucna_rijec in kljucne_rijeci):
            return kategorija

    # Default kategorija ako se ne pronađe ništa
    return 'Razne vijesti'



def contact(request):
    context = {
         'naslov_stranice': 'Kontakt - Time.ba',
    }
    return render(request, 'kontakt.html', context)

def prognoza(request):
    context = {
         'naslov_stranice': 'Prognoza - Time.ba',
    }
    return render(request, 'prognoza.html', context)

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


def news_archive(request):
    date = request.GET.get('date')
    if date:
        # Pretvaranje stringa datuma u objekat datuma i filtriranje vijesti
        news_items = Headlines.objects.filter(published_date__date=date)
    else:
        news_items = Headlines.objects.all()

    # Pretvaranje vijesti u JSON format
    news_list = [{'title': news.title, 'description': news.description} for news in news_items]

    return JsonResponse(news_list, safe=False)

def widget(request):
    context = {
         'naslov_stranice': 'Widget - Time.ba',
    }
    return render(request, 'widget.html', context)

def rsspage(request):
    context = {
         'naslov_stranice': 'Rss - Time.ba',
    }
    return render(request, 'rss.html', context)

def mobile(request):
    context = {
         'naslov_stranice': 'Mobile - Time.ba',
    }
    return render(request, 'mobile/index.html', context)




def company_directory(request):
    file_paths = [
        settings.BASE_DIR / 'static' / 'Baza 2000.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2001.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2003.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2005.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2006.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2007.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2008.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2009.xlsx',
    ]
    # Dobijanje broja firmi po opštinama
    companies_count_by_city = create_company_directory_adjusted(file_paths)  # Ispravljeno ime varijable

    context = {
        'companies_count_by_city': companies_count_by_city,  # Ispravljeno ime ključa u kontekstu
    }
    return render(request, 'firme.html', context)

def city_companies(request, city_name):
    # Pretpostavljamo da city_name dolazi iz URL-a i koristit ćemo ga za filtriranje podataka
    file_paths = [
        settings.BASE_DIR / 'static' / 'Baza 2000.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2001.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2003.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2005.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2006.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2007.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2008.xlsx',
        settings.BASE_DIR / 'static' / 'Baza 2009.xlsx',
    ]
    all_data = pd.DataFrame()
    
 
    for fp in file_paths:
        # Ovdje pretpostavljamo da fajl sadrži kolonu 'Opština' koja sadrži nazive opština
        data = pd.read_excel(fp)
        # Ako su nazivi kolona validni, nema potrebe za dodatnim preimenovanjem
        all_data = pd.concat([all_data, data], ignore_index=True)
    
    # Ako 'city_name' nije u ispravnom formatu, pretvorite ga u string
    city_name_str = str(city_name).strip()
    
    # Filtriranje podataka za odabranu opštinu
    city_companies_data = all_data[all_data['Opština'].str.contains(city_name_str, na=False)]
    
    companies_list = []
    for company in city_companies_data.to_dict('records'):
        company_dict = {key.replace(' ', '_'): value for key, value in company.items()}
        companies_list.append(company_dict)

    context = {
        'companies': companies_list,
        'city_name': city_name,
    }
    
    return render(request, 'city_companies.html', context)