# Generated by Django 5.0 on 2024-01-13 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timee', '0012_lastfetchtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='headlines',
            name='source_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
