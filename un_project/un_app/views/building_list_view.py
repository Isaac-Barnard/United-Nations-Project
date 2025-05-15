from django.shortcuts import render
from django.db.models import F, FloatField, ExpressionWrapper, Value, Window
from django.db.models.functions import Coalesce, Rank
from ..models import Building

def building_list(request):
    # Annotate the queryset with the calculated height, handling null values
    buildings = Building.objects.select_related('owner', 'territory').annotate(
        # Use Coalesce to handle nulls, defaulting to 0
        calculated_height=ExpressionWrapper(
            Coalesce(F('y_level_high_pt'), Value(0)) - Coalesce(F('y_level_ground'), Value(0)),
            output_field=FloatField()
        ),
        # Add rank based on calculated height
        rank=Window(
            expression=Rank(),
            order_by=F('calculated_height').desc()
        )
    ).order_by('-calculated_height')

    return render(request, 'building_list.html', {'buildings': buildings})