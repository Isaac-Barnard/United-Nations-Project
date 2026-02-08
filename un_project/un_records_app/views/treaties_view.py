from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from ..models import Treaty

def treaties(request):
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    treaties = Treaty.objects.prefetch_related('images').all().order_by('-date')
    return render(request, 'treaties.html', {'treaties': treaties})


def treaty_detail(request, slug):
    treaty = get_object_or_404(Treaty.objects.prefetch_related('images').order_by('-date'), slug=slug)

    return render(request, 'treaty_detail.html', {'treaty': treaty})