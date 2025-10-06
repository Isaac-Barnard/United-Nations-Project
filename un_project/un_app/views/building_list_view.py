from django.shortcuts import render
from django.db.models import F, FloatField, ExpressionWrapper, Value, Window, Min, Q
from django.db.models.functions import Coalesce, RowNumber
from ..models import Building

def building_list(request):
    sort = request.GET.get('sort', 'calculated_height')
    direction = request.GET.get('dir', 'desc')
    search_query = request.GET.get('search', '').strip()

    order_prefix = '' if direction == 'asc' else '-'
    order_by = f'{order_prefix}{sort}'

    # Start with base queryset
    buildings = Building.objects.select_related('owner', 'territory').prefetch_related('main_builders')

    # Apply search filter if provided
    if search_query:
        buildings = buildings.filter(
            Q(name__icontains=search_query) |
            Q(territory__name__icontains=search_query) |
            Q(owner__abbreviation__icontains=search_query) |
            Q(owner__name__icontains=search_query)
        )

    # Annotate with calculated_height and first_builder
    buildings = buildings.annotate(
        calculated_height=ExpressionWrapper(
            Coalesce(F('y_level_high_pt'), Value(0)) - Coalesce(F('y_level_ground'), Value(0)),
            output_field=FloatField()
        ),
        first_builder=Min('main_builders__username')
    ).order_by(order_by)

    return render(request, 'building_list.html', {
        'buildings': buildings,
        'current_sort': sort,
        'current_dir': direction,
        'search_query': search_query,
    })