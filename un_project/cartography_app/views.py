from django.shortcuts import render
from django.db.models import Prefetch
from .models import *
from django.shortcuts import get_object_or_404, render

def cartography_home(request):
    return render(request, 'cartography_home.html')

def interactive_un_map(request):
    return render(request, 'interactive_un_map.html')


def historical_maps(request):
    map_type = request.GET.get("type", "Official")
    maps = (CartographyMap.objects.filter(type=map_type).order_by("-map_date"))

    return render(request, "historical_maps.html", {
        "maps": maps,
        "current_type": map_type,
    })



def historical_map_detail(request, slug):
    map_obj = get_object_or_404(CartographyMap, slug=slug)

    return render(request, "historical_map_detail.html", {
        "map": map_obj,
    })