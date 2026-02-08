from django.shortcuts import render
from ..models import Petition

def petitions(request):
    petition_type = request.GET.get('type')
    petitions = Petition.objects.prefetch_related('images').order_by('-date')
    
    if petition_type:
        petitions = petitions.filter(petition_type=petition_type)

    # To generate buttons, get unique petition types
    petition_types = Petition.objects.values_list('petition_type', flat=True).distinct()
    
    return render(request, 'petitions.html', {
        'petitions': petitions,
        'petition_types': petition_types,
        'current_type': petition_type
    })