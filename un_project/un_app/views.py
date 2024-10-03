from django.shortcuts import render
from django.db.models import F, FloatField, ExpressionWrapper, Count, Value
from django.db.models.functions import Coalesce
from .models import Building, Player

def home(request):
    return render(request, 'home.html')


def building_list(request):
    # Annotate the queryset with the calculated height, handling null values
    buildings = Building.objects.select_related('owner', 'territory').annotate(
        # Use Coalesce to handle nulls, defaulting to 0
        calculated_height=ExpressionWrapper(
            Coalesce(F('y_level_high_pt'), Value(0)) - Coalesce(F('y_level_ground'), Value(0)),
            output_field=FloatField()
        )
    ).order_by('-calculated_height')  # Sort by calculated height

    return render(request, 'building_list.html', {'buildings': buildings})


def player_list(request):
    players = Player.objects.select_related('nation').annotate(
        num_buildings_built=Count('main_builds')
    ).order_by('-num_buildings_built')  # Sort by the number of buildings built in descending order
    return render(request, 'player_list.html', {'players': players})
