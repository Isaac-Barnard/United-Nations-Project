from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from ..models import CourtCase, CourtCaseArgument, CourtCaseArgumentImage, CourtCaseArgumentVideo

def court_cases(request):
    images_prefetch = Prefetch('images',queryset=CourtCaseArgumentImage.objects.all().order_by('order'))
    videos_prefetch = Prefetch('videos', queryset=CourtCaseArgumentVideo.objects.all().order_by('order'))
    arguments_prefetch = Prefetch('case_argued',queryset=CourtCaseArgument.objects.all().order_by('number').prefetch_related(images_prefetch, videos_prefetch),to_attr='arguments')
    court_cases = (CourtCase.objects.prefetch_related(arguments_prefetch).all().order_by('-date'))
    
    # Annotate first special argument in each case
    for case in court_cases:
        ruling_time = False
        for arg in case.arguments:
            if not ruling_time and arg.argument_type in ["Dissenting Opinion", "Concurring Opinion"]:
                arg.is_ruling_time = True
                ruling_time = True
            else:
                arg.is_ruling_time = False
                
    return render(request, 'court_cases.html', {'court_cases': court_cases})


def court_case_detail(request, slug):
    images_prefetch = Prefetch(
        'images',
        queryset=CourtCaseArgumentImage.objects.all().order_by('order')
    )
    videos_prefetch = Prefetch(
        'videos',
        queryset=CourtCaseArgumentVideo.objects.all().order_by('order')
    )
    arguments_prefetch = Prefetch(
        'case_argued',
        queryset=CourtCaseArgument.objects.all()
            .order_by('number')
            .prefetch_related(images_prefetch, videos_prefetch),
        to_attr='arguments'
    )

    case = get_object_or_404(
        CourtCase.objects.prefetch_related(arguments_prefetch),
        slug=slug
    )

    ruling_time = False
    for arg in case.arguments:
        if not ruling_time and arg.argument_type in ["Dissenting Opinion", "Concurring Opinion"]:
            arg.is_ruling_time = True
            ruling_time = True
        else:
            arg.is_ruling_time = False

    return render(request, 'court_case_detail.html', {'case': case})