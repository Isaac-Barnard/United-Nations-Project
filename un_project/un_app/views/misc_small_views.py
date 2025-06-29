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


from ..models import Building, Nation, Player, Territory

@login_required
def input_building(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('building_success')  # or wherever you want
    else:
        form = BuildingForm()
    
    # Get unique values from existing buildings
    territories = Territory.objects.all()
    owners = Nation.objects.all()
    
    context = {
        'form': form,
        'territories': territories,
        'owners': owners,
    }
    return render(request, 'input_building.html', context)


def general_territory_info(request):
    return render(request, 'general_territory_info.html')