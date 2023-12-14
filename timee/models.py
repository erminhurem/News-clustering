from django.db import models

class Headlines(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField(max_length=5000)
    description = models.TextField()
    published_date = models.DateTimeField()
    category = models.CharField(max_length=200, null=True, blank=True)
    source = models.CharField(max_length=100)
    image_urls= models.URLField(max_length=1000,default=None,blank=True, null=True)

    def __str__(self):
        return self.title