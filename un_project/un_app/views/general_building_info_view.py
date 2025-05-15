from django.shortcuts import render
from django.db.models import Count
from ..models import Building, Nation
from collections import defaultdict
from datetime import datetime

def general_building_info(request):
    current_year = datetime.now().year
    years = list(range(2019, current_year + 1))

    buildings = Building.objects.filter(year_started__isnull=False).select_related('owner')
    nations = Nation.objects.all()

    # Precompute per-year counts for all buildings
    per_year_counts = buildings.values('owner__id', 'year_started').annotate(count=Count('id'))

    # Reformat per-year counts into a dict
    per_nation_data = defaultdict(lambda: {year: 0 for year in years})
    for row in per_year_counts:
        nation_id = row['owner__id']
        year = row['year_started']
        if year in years:
            per_nation_data[nation_id][year] = row['count']

    # Assemble table data per nation
    table_data = []
    all_heights = []  # Track all heights globally
    total_avg_per_year = 0  # Initialize variable for avg buildings per year
    
    for nation in nations:
        nation_buildings = [b for b in buildings if b.owner_id == nation.id]

        # Calculate stats
        heights = [b.height for b in nation_buildings if b.height > 0]
        all_heights.extend(heights)  # Accumulate into global list
        
        avg_height = round(sum(heights) / len(heights), 3) if heights else None
        total = len(nation_buildings)
        yearly_counts = [per_nation_data[nation.id][y] for y in years]

        # Special treatment for New Belize
        is_new_belize = nation.name == "New Belize"
        
        # Calculate avg_per_year, excluding 2019-2021 for New Belize
        if is_new_belize:
            # Filter years excluding 2019, 2020, 2021 for New Belize
            valid_years = [y for y in years if y not in (2019, 2020, 2021)]
            valid_years_count = len(valid_years)
            
            # Use only valid years for calculation
            if valid_years_count > 0:
                # Only count buildings in valid years
                valid_buildings = sum(per_nation_data[nation.id][y] for y in valid_years)
                avg_per_year = round(valid_buildings / valid_years_count, 2)
            else:
                avg_per_year = 0
        else:
            # Normal calculation for other nations
            total_years = len(years)
            if total_years > 0:
                avg_per_year = round(total / total_years, 2)
            else:
                avg_per_year = 0
        
        total_avg_per_year += avg_per_year  # Accumulate avg_per_year for overall avg

        table_data.append({
            'nation': nation.name,
            'avg_height': avg_height,
            'total_buildings': total,
            'yearly_counts': yearly_counts,
            'avg_per_year': avg_per_year,
            'is_new_belize': is_new_belize  # Flag to handle in template
        })

    # Calculate total row
    totals_per_year = [sum(row['yearly_counts'][i] for row in table_data) for i in range(len(years))]
    total_buildings = sum(row['total_buildings'] for row in table_data)
    
    # Calculate overall avg height (across all buildings with height > 0)
    if all_heights:
        total_avg_height = round(sum(all_heights) / len(all_heights), 3)
    else:
        total_avg_height = None
        
    # Calculate total avg buildings per year (average of avg_per_year)
    if len(nations) > 0:
        total_avg_per_year = round(total_avg_per_year / len(nations), 1)
    else:
        total_avg_per_year = None

    context = {
        'table_data': table_data,
        'years': years,
        'totals_per_year': totals_per_year,
        'total_buildings': total_buildings,
        'total_avg_height': total_avg_height,
        'total_avg_per_year': total_avg_per_year,
    }
    return render(request, 'general_building_info.html', context)
