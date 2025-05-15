from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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
    return render(request, 'input_building.html')


def general_territory_info(request):
    return render(request, 'general_territory_info.html')