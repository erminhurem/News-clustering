import feedparser
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from dateutil import parser as date_parser
from django.utils.timezone import make_aware, now
from .models import Headlines
from bs4 import BeautifulSoup
from django.db.models import Count
import datetime

# Pomoćna funkcija za pretvaranje URL-a izvora u prijateljsko ime
def get_friendly_source_name(url):
    if 'telegraf.rs' in url:
        return 'Telegraf'
    elif 'kurir.rs' in url:
        return 'Kurir'
    elif 'nova.rs' in url:
        return 'Nova'
    elif 'n1info.ba' in url:
        return 'N1'
    # Dodajte više uslova za ostale izvore
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

def index(request):
    latest_news = Headlines.objects.all().order_by('-published_date')[:3]
    for news in latest_news:
        news.source_name = get_friendly_source_name(news.source)
        news.time_since = get_relative_time(news.published_date)

    categories = ['Ekonomija', 'Sport', 'BiH', 'Balkan', 'Svijet', 'Hronika', 'Sarajevo', 'Kultura', 'Scena', 'Sport', 'Magazin']
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




def fetch_news():
    feeds = [
        'https://www.telegraf.rs/rss',
        'https://www.kurir.rs/rss',
        'https://nova.rs/rss',
        'https://n1info.ba/feed/',
        'https://www.euronews.rs/rss',
        'https://informer.rs/rss',
        'https://n1info.ba/rss',
        'https://n1info.hr/rss'
    ]

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
                news_item.save()

def categorize_news(url):
    if 'ekonomija' in url:
        return 'Ekonomija'
    elif 'sport' in url:
        return 'Sport'
    
    elif 'srbija' in url:
        return 'Srbija'
    # Ovdje dodaj dodatne kategorije prema potrebi
    return 'Ostalo'
