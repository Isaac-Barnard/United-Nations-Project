from django.shortcuts import render
from django.db.models import F, FloatField, ExpressionWrapper, Count
from .models import Building, Player

def building_list(request):
    # Annotate the queryset with the calculated height
    buildings = Building.objects.select_related('owner', 'territory').annotate(
        # sort by height
        calculated_height=ExpressionWrapper(
            F('y_level_high_pt') - F('y_level_ground'),  # Calculate height
            output_field=FloatField()
        )
    ).order_by('-calculated_height')  # Sort by calculated height
    return render(request, 'building_list.html', {'buildings': buildings})


def player_list(request):
    players = Player.objects.select_related('nation').annotate(
        num_buildings_built=Count('main_builds')
    ).order_by('-num_buildings_built')  # Sort by the number of buildings built in descending order
    return render(request, 'player_list.html', {'players': players})
