from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from ..models import Resolution,  ResolutionAmendment

def resolutions(request):
    amendments_prefetch = Prefetch('amended_resolution',queryset=ResolutionAmendment.objects.all().order_by('date'),to_attr='amendments')
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    resolutions = (Resolution.objects.prefetch_related('images', amendments_prefetch).all().order_by('-date'))
    return render(request, 'resolutions.html', {'resolutions': resolutions})


def resolution_detail(request, slug):
    amendments_prefetch = Prefetch('amended_resolution', queryset=ResolutionAmendment.objects.order_by('date'), to_attr='amendments')

    resolution = get_object_or_404(Resolution.objects.prefetch_related('images', amendments_prefetch), slug=slug)

    return render(request, 'resolution_detail.html', {'resolution': resolution})