from django.shortcuts import render
from django.db.models import F, FloatField, ExpressionWrapper, Value, Window, Min
from django.db.models.functions import Coalesce, RowNumber
from ..models import Building

def building_list(request):
    sort = request.GET.get('sort', 'calculated_height')
    direction = request.GET.get('dir', 'desc')

    order_prefix = '' if direction == 'asc' else '-'
    order_by = f'{order_prefix}{sort}'

    # First, annotate with calculated_height and first_builder
    buildings = Building.objects.select_related('owner', 'territory').prefetch_related('main_builders').annotate(
        calculated_height=ExpressionWrapper(
            Coalesce(F('y_level_high_pt'), Value(0)) - Coalesce(F('y_level_ground'), Value(0)),
            output_field=FloatField()
        ),
        first_builder=Min('main_builders__username')  # Get the first builder alphabetically
    ).order_by(order_by)

    return render(request, 'building_list.html', {
        'buildings': buildings,
        'current_sort': sort,
        'current_dir': direction,
    })