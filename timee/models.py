from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Headlines(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField(max_length=5000)
    description = models.TextField()
    published_date = models.DateTimeField()
    category = models.CharField(max_length=200, null=True, blank=True)
    source = models.CharField(max_length=100)
    image_urls = models.URLField(
        max_length=1000, default=None, blank=True, null=True)
    related_news = models.ManyToManyField(
        'self', symmetrical=False, related_name='related_by', blank=True)
    source_name = models.CharField(max_length=200, blank=True, null=True)
    other_sources = models.ManyToManyField('Source', related_name='headlines')

    def __str__(self):
        return self.title


@receiver(pre_save, sender=Headlines)
def postavi_podrazumevanu_sliku(sender, instance, **kwargs):
    if not instance.image_urls:  # Ako slika nije učitana
        instance.image_urls = 'static\images\no_image.png'


class Source(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField()

    def __str__(self):
        return self.name


class LastFetch(models.Model):
    last_update_time = models.DateTimeField(default=None,)

    @classmethod
    def update_last_fetch_time(cls):
        # Ažuriranje ili stvaranje novog zapisa s trenutnim vremenom
        last_fetch, created = cls.objects.get_or_create(
            id=1, defaults={'last_update_time': timezone.now()})
        if not created:
            last_fetch.last_update_time = timezone.now()
            last_fetch.save()

    @classmethod
    def get_last_update_time(cls):
        # Dobavljanje zadnjeg ažuriranog vremena, ili vraćanje None ako ne postoji zapis
        return cls.objects.last().last_update_time if cls.objects.exists() else None


class Firme(models.Model):
    id_broj = models.CharField(max_length=100, default=None)
    naziv_kompanije = models.CharField(max_length=100, default=None)
    adresa = models.CharField(max_length=50, default=None)
    sifra = models.IntegerField(default=None)
    opstina = models.CharField(max_length=50, default=None)

    def __str__(self):
        return self.naziv_kompanije
