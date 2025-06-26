from django.shortcuts import render
from django.db.models import Prefetch
from .models import Resolution, Treaty, Executive_Order, ResolutionAmendment, Charter, CharterAmendment , Alliance

# Create your views here.
def records_home(request):
    return render(request, 'records_home.html')

def charter(request):
    charter = Charter.objects.prefetch_related(Prefetch('amended_charter', queryset=CharterAmendment.objects.order_by('date'))).order_by('-date')
    return render(request, 'charter.html', {'charter': charter})

def resolutions(request):
    amendments_prefetch = Prefetch('amended_resolution',queryset=ResolutionAmendment.objects.all().order_by('date'),to_attr='amendments')
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    resolutions = (Resolution.objects.prefetch_related('images', amendments_prefetch).all().order_by('-date'))
    return render(request, 'resolutions.html', {'resolutions': resolutions})

def court_cases(request):
    return render(request, 'court_cases.html')

def treaties(request):
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    treaties = Treaty.objects.prefetch_related('images').all().order_by('-date')
    return render(request, 'treaties.html', {'treaties': treaties})

def executive_orders(request):
    executive_orders = Executive_Order.objects.all().order_by('-charter', '-date')
    return render(request, 'executive_orders.html', {'executive_orders': executive_orders})

def alliances(request):
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    alliances = Alliance.objects.prefetch_related('images').all().order_by('-date')
    return render(request, 'alliances.html', {'alliances': alliances})

def declaration_of_wars(request):
    return render(request, 'declaration_of_wars.html')