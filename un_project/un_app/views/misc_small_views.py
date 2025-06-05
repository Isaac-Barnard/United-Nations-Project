from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import BuildingForm


def home(request):
    return render(request, 'home.html')


def financial_home(request):
    return render(request, 'financial_home.html')


def evaluation_success(request):
    return render(request, 'evaluation_success.html')


def un_map(request):
    return render(request, 'un_map.html')


@login_required
def input_building(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('building_success')  # Replace with your desired success URL
    else:
        form = BuildingForm()
    
    return render(request, 'input_building.html', {'form': form})


def general_territory_info(request):
    return render(request, 'general_territory_info.html')