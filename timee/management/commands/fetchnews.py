from django.core.management.base import BaseCommand
from timee.views import fetch_news

class Command(BaseCommand):
    help = 'Fetches the news from the RSS feeds'

    def handle(self, *args, **options):
        fetch_news()
        self.stdout.write(self.style.SUCCESS('Successfully fetched news'))


