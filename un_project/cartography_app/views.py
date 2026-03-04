from django.shortcuts import render
from django.db.models import Prefetch
from .models import *

def cartography_home(request):
    return render(request, 'cartography_home.html')

def interactive_un_map(request):
    return render(request, 'interactive_un_map.html')


def historical_maps(request):
    map_type = request.GET.get("type", "Official")
    maps = (CartographyMap.objects.filter(type=map_type).order_by("-map_date"))
    context = {"maps": maps,"current_type": map_type,}
    return render(request, "historical_maps.html", context)