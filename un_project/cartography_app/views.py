from django.shortcuts import render
from django.db.models import Prefetch
from .models import *

# Create your views here.
def cartography_home(request):
    return render(request, 'cartography_home.html')