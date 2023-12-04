from django.db import models

class Headlines(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
    description = models.TextField()
    published_date = models.DateTimeField()
    source = models.CharField(max_length=100)
    image_urls= models.URLField(default=None,blank=True, null=True)

    def str(self):
        return self.title