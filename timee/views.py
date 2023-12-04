import feedparser
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from dateutil import parser as date_parser
from .models import Headlines
from bs4 import BeautifulSoup
from django.db.models import Count

def index(request):
    # Dohvati tri najnovije vijesti
    latest_news = Headlines.objects.all().order_by('-published_date')[:3]

    # Definiše kategorije i pridružuje im jedinstvene ID-eve
    categories = ['Ekonomija', 'Sport', 'Srbija', 'Ostalo']
    category_ids = {category: f'c{idx+1}' for idx, category in enumerate(categories)}

    # Dohvati po tri vijesti za svaku kategoriju
    news_by_category = {}
    for category in categories:
        news_by_category[category] = Headlines.objects.filter(category=category).order_by('-published_date')[:3]

    # Pakuj sve potrebne informacije u kontekst
    context = {
        'latest_news': latest_news,
        'news_by_category': news_by_category,
        'category_ids': category_ids,
    }

    # Renderuj šablon sa kontekstom
    return render(request, "index.html", context)



def fetch_news():
    feeds = [
        'https://www.telegraf.rs/rss',
        'https://www.kurir.rs/rss',
        'https://nova.rs/rss',
        'https://n1info.ba/feed/'
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
    # Ovdje dodajte dodatne kategorije prema potrebi
    return 'Ostalo'
