import feedparser
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from dateutil import parser as date_parser
from .models import Headlines
from bs4 import BeautifulSoup




def index(request):

    fetch_news()

    headlines = Headlines.objects.all()

    for headline in headlines:
        if headline.image_urls:
            headline.image_urls = headline.image_urls.split(',')

    return render(request, "index.html", {'headlines': headlines})

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

                # Parse HTML content to extract images
                content = entry.content[0].value if 'content' in entry else ''
                soup = BeautifulSoup(content, 'html.parser')
                images = soup.find_all('img')  # Find all img tags

                # Store image URLs in a list
                image_urls = [img['src'] for img in images]

                news_item = Headlines(
                    title=entry.title,
                    link=entry.link,
                    description=entry.description,
                    published_date=published_date,
                    source=feed_url,
                    
                    image_urls=','.join(image_urls) if image_urls else None
                )
                news_item.save()