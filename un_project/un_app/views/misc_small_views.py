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


from ..models import Denomination
def currency_converter(request):
    denominations = Denomination.objects.all().order_by('priority')
    return render(request, 'currency_converter.html', {'denominations': denominations,})


from django.shortcuts import render
from ..models import Item

def item_value_calculator(request):
    all_items = Item.objects.all().order_by('ordering')
    items_parts = [[] for _ in range(5)]
    for item in all_items:
        idx = (item.ordering // 100) - 1
        if 0 <= idx < 5:
            items_parts[idx].append(item)
    return render(request, 'item_value_calculator.html', {'items_parts': items_parts})
