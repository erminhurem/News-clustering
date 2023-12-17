from django.shortcuts import render
from .models import Headlines

def prikaz_izvora(request, naziv_izvora):
    vijesti = Headlines.objects.filter(source=naziv_izvora).order_by('-published_date')
    context = {
        'naslov_stranice': f'{naziv_izvora.capitalize()} - Time.ba',
        'vijesti': vijesti,
    }
    return render(request, 'izvori.html', context)

def svi_izvori(request):
    context = {
        'naslov_stranice': 'Izvori - Time.ba',
    }
    return render(request, 'izvori.html', context)
