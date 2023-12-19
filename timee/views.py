import feedparser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from dateutil import parser as date_parser
from django.utils.timezone import make_aware, now
from .models import Headlines, Source
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta 
from dateutil.parser import parse as parse_date
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
from django.utils.timezone import now
from collections import defaultdict
from datetime import datetime, time
import html
from django.shortcuts import get_object_or_404, render
nltk.download('punkt')

def get_or_create_sources_for_news(news):
    # Ovdje definirajte logiku za identificiranje izvora za određenu vijest
    # Na primjer, možete koristiti ključne riječi iz opisa vijesti

    # Pretpostavimo da imate listu ključnih riječi koje odgovaraju različitim izvorima
    keywords_to_sources = {
        'ključna riječ 1': 'Izvor 1',
        'ključna riječ 2': 'Izvor 2',
        # Dodajte ostale parove ključna riječ - izvor
    }

    sources = []
    for keyword, source_name in keywords_to_sources.items():
        if keyword in news.description:
            source, created = Source.objects.get_or_create(name=source_name, link='URL za izvor')
            sources.append(source)

    return sources


def related_news_view(request, pk):
    news = get_object_or_404(Headlines, pk=pk)
    related_news = news.related_news.all()

    for news in related_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    return render(request, 'povezane_vijesti.html', {'related_news': related_news})

def news_at_10(request):
    today = datetime.now().date()

    # Postavljanje vremena na 10:00 ujutro
    start_time = datetime.combine(today, time(10, 0))  # 10:00 ujutro

    # Postavljanje vremena na 10:59 ujutro
    end_time = datetime.combine(today, time(10, 59))  # 10:59 ujutro

    # Filtriramo vijesti objavljene između 10:00 i 10:59
    news_at_10 = Headlines.objects.filter(published_date__gte=start_time, published_date__lte=end_time).order_by('-published_date')

    # Dodavanje dodatnih informacija vijestima
    for news in news_at_10:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)
        news.related_news_list = list(news.related_news.all())

    # Dohvat vijesti po kategorijama
    categories = ['Ekonomija', 'BiH', 'Balkan', 'Svijet', 'Hronika', 'Sarajevo', 'Kultura', 'Scena', 'Sport', 'Magazin']
    news_by_category = {}
    for category in categories:
        news_items = Headlines.objects.filter(category=category).order_by('-published_date')[:3]
        for item in news_items:
            item.source_name = get_friendly_source_name(item.source)
            item.time_since = get_relative_time(item.published_date)
        news_by_category[category] = news_items

    # Postavljanje konteksta za template
    context = {
        'news_at_10': news_at_10,
        'naslov_stranice': 'Vijesti u 10 Sati - Time.ba',
        'news_by_category': news_by_category,
    }

    return render(request, "10h.html", context)


def news_last_17_hours(request):
    # Trenutno vrijeme minus 17 sati
    time_threshold = datetime.now() - timedelta(hours=17)

    # Filtriramo vijesti objavljene u proteklih 17 sati
    recent_news = Headlines.objects.filter(published_date__gte=time_threshold).order_by('-published_date')

    for news in recent_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Dodajte ostale potrebne elemente u kontekst ako je potrebno
    context = {
        'recent_news': recent_news,
        'naslov_stranice': 'Nedavne Vijesti - Time.ba',
    }

    return render(request, "17h.html", context)





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
    elif 'mondo.ba' in url:
        return 'Mondo'
    elif 'namaz.ba' in url:
        return 'Namaz'
    elif 'b92.net' in url:
        return 'B92'
    elif 'espreso.co.rs' in url:
        return 'espreso.co.rs'
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

def clean_description(description):
    # Dekodiranje HTML entiteta
    decoded_html = html.unescape(description)
    
    # Uklanjanje HTML tagova koristeći BeautifulSoup
    soup = BeautifulSoup(decoded_html, 'html.parser')
    
    # Uklanjanje svih tagova
    for tag in soup.findAll(True):
        tag.decompose()
    
    # Dobijanje čistog teksta
    cleaned_text = soup.get_text(separator=' ')
    
    return cleaned_text

def extract_keywords(text):
    words = nltk.word_tokenize(text)
    keywords = [word for word in words if word.isalnum()]
    return keywords



# početak koda vezano za rubriku Vijesti
def index(request):
    latest_news = Headlines.objects.all().order_by('-published_date')[:3]
    all_news = Headlines.objects.all().order_by('-published_date')
    vectorizer = TfidfVectorizer()
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
    [' '.join(extract_keywords(clean_description(news.description))) for news in all_news]
  )

    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(clean_description(news.description)))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [all_news[i.item()].id for i in related_articles_indices if all_news[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

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
    vectorizer = TfidfVectorizer()
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)   
    
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_items]
    )

    for news in news_items:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_items[i.item()].id for i in related_articles_indices if news_items[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

    context = {
        'news_by_category': {'BiH': news_page},
        'naslov_stranice': 'BiH - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "bih_category.html", context)

def ekonomija_category(request):
    news_items = Headlines.objects.filter(category='Ekonomija').order_by('-published_date')
    vectorizer = TfidfVectorizer()
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)   
    
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_items]
    )

    for news in news_items:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_items[i.item()].id for i in related_articles_indices if news_items[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

    
    context = {
        'news_by_category': {'Ekonomija': news_page},
        'naslov_stranice': 'Ekonomija - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "ekonomija_category.html", context)

def balkan_category(request):
    news_items = Headlines.objects.filter(category='Balkan').order_by('-published_date')

    vectorizer = TfidfVectorizer()
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)   
    
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_items]
    )

    for news in news_items:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_items[i.item()].id for i in related_articles_indices if news_items[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

    context = {
        'news_by_category': {'Balkan': news_page},
        'naslov_stranice': 'Balkan - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "balkan_category.html", context)

def svijet_category(request):
    news_items = Headlines.objects.filter(category='Svijet').order_by('-published_date')
    vectorizer = TfidfVectorizer()
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)   
    
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_items]
    )

    for news in news_items:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_items[i.item()].id for i in related_articles_indices if news_items[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

    context = {
        'news_by_category': {'Svijet': news_page},
        'naslov_stranice': 'Svijet - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "svijet_category.html", context)

def sarajevo_category(request):
    news_items = Headlines.objects.filter(category='Sarajevo').order_by('-published_date')
    vectorizer = TfidfVectorizer()
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)   
    
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_items]
    )

    for news in news_items:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_items[i.item()].id for i in related_articles_indices if news_items[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

    context = {
        'news_by_category': {'Sarajevo': news_page},
        'naslov_stranice': 'Sarajevo - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "sarajevo_category.html", context)

def hronika_category(request):
    news_items = Headlines.objects.filter(category='Hronika').order_by('-published_date')
    vectorizer = TfidfVectorizer()
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)   
    
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_items]
    )

    for news in news_items:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_items[i.item()].id for i in related_articles_indices if news_items[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

    context = {
        'news_by_category': {'Hronika': news_page},
        'naslov_stranice': 'Hronika - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "hronika_category.html", context)

def kultura_category(request):
    news_items = Headlines.objects.filter(category='Kultura').order_by('-published_date')
    vectorizer = TfidfVectorizer()
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)   
    
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_items]
    )

    for news in news_items:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_items[i.item()].id for i in related_articles_indices if news_items[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

    context = {
        'news_by_category': {'Kultura': news_page},
        'naslov_stranice': 'Kultura - Time.ba',
        'latest_news': news_page.object_list,
    }
    return render(request, "kultura_category.html", context)

def scena_category(request):
    news_items = Headlines.objects.filter(category='Scena').order_by('-published_date')
    vectorizer = TfidfVectorizer()
    
    items_per_page = 10
    paginator = Paginator(news_items, items_per_page)
    page = request.GET.get("page")

    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        
        news_page = paginator.page(1)
    except EmptyPage:
        
        news_page = paginator.page(paginator.num_pages)   
    
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_items]
    )

    for news in news_items:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_items[i.item()].id for i in related_articles_indices if news_items[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

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
    vectorizer = TfidfVectorizer()

    for news_m in latest_news_m:
        news_m.source_name = get_friendly_source_name(news_m.source)
        news_m.time_since = get_relative_time(news_m.published_date)

    latest_news = Headlines.objects.all().order_by("-published_date")[:3]
    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)
    
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in latest_news_m] )

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [latest_news_m[i.item()].id for i in related_articles_indices if latest_news_m[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

    categories = ['Zabava', 'Automobili', 'Tehnologija', 'Lifestyle','Hrana','Intima', 'VIJESTI','SPORT']
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
    vectorizer = TfidfVectorizer()

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

       
    # Izračunavanje TF-IDF vektora za 'description' polje
    tfidf_matrix = vectorizer.fit_transform(
        [' '.join(extract_keywords(news.description)) for news in news_page] )

    # Izračunavanje TF-IDF vektora za trenutnu vijest
    current_tfidf = vectorizer.transform(
        [' '.join(extract_keywords(news.description))]
    )
    cosine_similarities = cosine_similarity(current_tfidf, tfidf_matrix)

    # Dobivanje indeksa povezanih članaka
    related_articles_indices = cosine_similarities[0].argsort()[:-11:-1]


    # Dohvaćanje povezanih vijesti iz baze podataka
    related_news_ids = [news_page[i.item()].id for i in related_articles_indices if news_page[i.item()].id != news.id]
    news.related_news.set(related_news_ids)  # Ovo će postaviti povezane vijesti

    #psotavljanje dobijenih izvora
    sources = get_or_create_sources_for_news(news)
    news.other_sources.set(sources)

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
    latest_news = Headlines.objects.all().order_by('-published_date')[:10]
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
    
    
    # Paginacija
    items_per_page = 10
    paginator = Paginator(latest_news, items_per_page)
    page = request.GET.get("page")
    try:
        latest_news = paginator.page(page)
    except PageNotAnInteger:
        latest_news = paginator.page(1)
    except EmptyPage:
        latest_news = paginator.page(paginator.num_pages)
    
    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

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

    if 'vijesti.ba' in entry.link:
        if 'image' in entry and isinstance(entry.image, str):
            images.append(entry.image)

    return images


def parse_date(date_str):
    try:
        return parser.parse(date_str)
    except ValueError as e:
        logger.error(f"Greška prilikom parsiranja datuma: {e}")
        return None


def fetch_news():
    feeds = [
        'https://www.sd.rs/rss.xml',
        'https://www.blic.rs/rss/danasnje-vesti',
        'https://www.blic.rs/rss/Vesti/Politika',
        'https://www.blic.rs/rss/Vesti/Hronika',
        'https://www.blic.rs/rss/Slobodno-vreme/Zanimljivosti',
        'https://www.blic.rs/rss/IT',
        'https://www.telegraf.rs/rss',
        'https://www.kurir.rs/rss',
        'https://nova.rs/rss',
        'https://n1info.ba/feed/',
        'https://informer.rs/rss',
        'https://n1info.ba/rss',
        'https://n1info.hr/rss',
        'https://www.vijesti.ba/rss/svevijesti',
        'https://balkans.aljazeera.net/rss.xml',
        'https://www.klix.ba/rss',
        'https://www.avaz.ba/rss',
        'https://beta.rs/rss',
        'https://www.oslobodjenje.ba/feed',
        'https://okanal.oslobodjenje.ba/okanal/feed',
        'https://www.b92.net/feed/',
        'https://www.dnevnik.ba/feed',
        'https://namaz.ba/feed/',
        'https://www.nkp.ba/feed/',
        'https://www.rtvslon.ba/feed/',
        'https://www.sd.rs/rss.xml',
        'https://www.rts.rs/rss/ci.html',
        'https://nova.rs/feed',
        'https://www.euronews.rs/rss/sport',
        'https://www.euronews.rs/rss/srbija',
        'https://www.euronews.rs/rss/evropa',
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
        'https://mondo.rs/rss/629/Naslovna',

    ]
    logger = logging.getLogger(__name__)
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if not Headlines.objects.filter(link=entry.link).exists():
                published_date = parse_date(entry.published) if entry.published else None
           
                image_urls = extract_images(entry)  # Koristi definisanu funkciju za ekstrakciju slika
                category = categorize_news(entry.link)  # Ovdje dodajemo kategoriju
                description = clean_description(entry.description)  # Čišćenje opisa

                news_item = Headlines(
                    title=entry.title,
                    link=entry.link,
                    description=description,
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
        'Automobili': ['automobili', 'motori', 'auto'],
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
        'Zdravlje': ['zdravlje', 'hrana'],
        'Magazin': ['magazin'],
        'Scena': ['scena', 'showbiz'],
        'Vijesti': ['vijesti', 'vesti'],
        'Sport': ['sport']
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

def search_news(request):
    query = request.GET.get('q', '')
    news_results = Headlines.objects.filter(title__icontains=query) if query else Headlines.objects.all()
    last_updated = Headlines.objects.latest('published_date').published_date

    # Paginacija
    paginator = Paginator(news_results, 10)  # 10 vijesti po stranici, prilagodite prema potrebi
    page = request.GET.get('page', 1)
    news_page = paginator.get_page(page)

    context = {
        'news_results': news_page,
        'last_updated': last_updated,
        'total_results': paginator.count,
    }
    return render(request, 'pretraga_rezultat.html', context)