from django.shortcuts import render

# Create your views here.
def records_home(request):
    return render(request, 'records_home.html')

def charter(request):
    return render(request, 'charter.html')

def resolutions(request):
    return render(request, 'resolutions.html')

def court_cases(request):
    return render(request, 'court_cases.html')

def treaties(request):
    return render(request, 'treaties.html')