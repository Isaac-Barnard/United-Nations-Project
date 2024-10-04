from django.shortcuts import render, get_object_or_404
from django.db.models import F, FloatField, ExpressionWrapper, Count, Value, Sum
from django.db.models.functions import Coalesce
from .models import Building, Player, Nation, PartialBuildingOwnership
from decimal import Decimal

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


def nation_building_list(request, nation_abbreviation):
    # Get the nation by its abbreviation
    nation = get_object_or_404(Nation, abbreviation=nation_abbreviation)
    
    # Fetch all buildings owned by the nation (no need to annotate height or ownership here)
    buildings = Building.objects.filter(owner=nation)

    return render(request, 'nation_building_list.html', {'nation': nation, 'buildings': buildings})