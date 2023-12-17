from django.shortcuts import render
from .models import Headlines

def prikaz_izvora(request, kljucna_rijec):
    vijesti = Headlines.objects.filter(source__icontains=kljucna_rijec).order_by('-published_date')
    context = {
        'naslov_stranice': f'{kljucna_rijec.capitalize()} - Time.ba',
        'vijesti': vijesti,
    }
    return render(request, 'prikaz_izvora.html', context)


def svi_izvori(request):
    context = {
        'naslov_stranice': 'Izvori - Time.ba',
    }
    return render(request, 'izvori.html', context)
