from django.shortcuts import render
from django.db.models import Prefetch
from .models import *

def cartography_home(request):
    return render(request, 'cartography_home.html')

def interactive_un_map(request):
    return render(request, 'interactive_un_map.html')


def historical_maps(request):
    maps = CartographyMap.objects.all()  # ordered by Meta
    context = {"maps": maps,}
    return render(request, "historical_maps.html", context)