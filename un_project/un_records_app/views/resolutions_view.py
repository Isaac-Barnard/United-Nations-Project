from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, Q
from ..models import Resolution,  ResolutionAmendment

from django.shortcuts import render
from django.db.models import Prefetch, Q, Case, When, Value, IntegerField
from ..models import Resolution, ResolutionAmendment

def resolutions(request):
    amendments_prefetch = Prefetch(
        'amended_resolution',
        queryset=ResolutionAmendment.objects.all().order_by('date'),
        to_attr='amendments'
    )

    query = request.GET.get('q', '')

    resolutions = Resolution.objects.prefetch_related(
        'images',
        amendments_prefetch
    ).all()

    if query:
        resolutions = resolutions.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query) |
            Q(amended_resolution__body__icontains=query)
        ).annotate(
            search_priority=Case(
                # Title match = highest priority
                When(title__icontains=query, then=Value(1)),

                # Body match = middle priority
                When(body__icontains=query, then=Value(2)),

                # Amendment match = lowest priority
                When(amended_resolution__body__icontains=query, then=Value(3)),

                default=Value(4),
                output_field=IntegerField(),
            )
        ).distinct().order_by('search_priority', '-date')

    else:
        resolutions = resolutions.order_by('-date')

    return render(
        request,
        'resolutions.html',
        {
            'resolutions': resolutions,
            'search_query': query,
        }
    )


def resolution_detail(request, slug):
    amendments_prefetch = Prefetch('amended_resolution', queryset=ResolutionAmendment.objects.order_by('date'), to_attr='amendments')

    resolution = get_object_or_404(Resolution.objects.prefetch_related('images', amendments_prefetch), slug=slug)

    return render(request, 'resolution_detail.html', {'resolution': resolution})