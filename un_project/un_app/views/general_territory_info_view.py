from django.shortcuts import render
from django.db.models import Count
from ..models import Building, Nation, Territory
from collections import defaultdict
from datetime import datetime

def general_territory_info(request):
    buildings = Building.objects.select_related('territory')
    territories = Territory.objects.all()
    nations = Nation.objects.all()

    # Assemble table data per territory
    table_data = []
    all_heights = []  # Track all heights globally
    
    for territory in territories:
        territory_buildings = [b for b in buildings if b.territory_id == territory.id]
        
        heights = [b.height for b in territory_buildings if b.height > 0]
        all_heights.extend(heights)  # Accumulate into global list
        
        avg_height = round(sum(heights) / len(heights), 3) if heights else None
        total = len(territory_buildings)
        
        # Get number of unique nations in a territory
        nations_in_territory = []
        for building in territory_buildings:
            nations_in_territory.append(building.owner)

        unique_nations = set(nations_in_territory)
        num_nations = len(unique_nations)
        
        table_data.append({
            'territory': territory.name,
            'total_buildings': total,
            'avg_height': avg_height,
            'num_nations': num_nations,
        })

    # Calculate total row
    total_buildings = sum(row['total_buildings'] for row in table_data)
    total_nations = len(nations)
    
    # Calculate overall avg height (across all buildings with height > 0)
    if all_heights:
        total_avg_height = round(sum(all_heights) / len(all_heights), 3)
    else:
        total_avg_height = None

    context = {
        'table_data': table_data,
        'total_buildings': total_buildings,
        'total_avg_height': total_avg_height,
        'total_nations': total_nations
    }
    #return render(request, 'general_building_info.html', context)
    return render(request, 'general_territory_info.html', context)
