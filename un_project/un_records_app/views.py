from django.shortcuts import render
from .models import Resolution, Treaty

# Create your views here.
def records_home(request):
    return render(request, 'records_home.html')

def charter(request):
    return render(request, 'charter.html')

def resolutions(request):
    resolutions = Resolution.objects.all().order_by('-date')
    return render(request, 'resolutions.html', {'resolutions': resolutions})

def court_cases(request):
    return render(request, 'court_cases.html')

def treaties(request):
    treaties = Treaty.objects.all().order_by('-date')
    return render(request, 'treaties.html', {'treaties': treaties})