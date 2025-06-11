from django.shortcuts import render
from .models import Resolution, Treaty, Executive_Order

# Create your views here.
def records_home(request):
    return render(request, 'records_home.html')

def charter(request):
    return render(request, 'charter.html')

def resolutions(request):
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    resolutions = Resolution.objects.prefetch_related('images').all().order_by('-date')
    return render(request, 'resolutions.html', {'resolutions': resolutions})

def court_cases(request):
    return render(request, 'court_cases.html')

def treaties(request):
# Prefetch images to avoid N+1 queries while maintaining date ordering
    treaties = Treaty.objects.prefetch_related('images').all().order_by('-date')
    return render(request, 'treaties.html', {'treaties': treaties})

def executive_orders(request):
    executive_orders = Executive_Order.objects.all().order_by('charter', '-date')
    return render(request, 'executive_orders.html', {'executive_orders': executive_orders})