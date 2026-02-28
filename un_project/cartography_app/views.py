from django.shortcuts import render
from django.db.models import Prefetch
from .models import *

def cartography_home(request):
    return render(request, 'cartography_home.html')

def interactive_un_map(request):
    return render(request, 'interactive_un_map.html')

def history_maps(request):
    return render(request, 'history_maps.html')