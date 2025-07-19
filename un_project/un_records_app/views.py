from django.shortcuts import render
from django.db.models import Prefetch
from .models import Resolution, Treaty, ExecutiveOrder, ResolutionAmendment, Charter, CharterAmendment , Alliance, DeclarationOfWar, NationalConstitution, NationalConstitutionAmendment, CourtCase, CourtCaseArgument, CourtCaseArgumentImage, CourtCaseArgumentVideo, Petition

# Create your views here.
def records_home(request):
    return render(request, 'records_home.html')

def un_staff(request):
    return render(request, 'un_staff.html')

def charter(request):
    charter = Charter.objects.prefetch_related(Prefetch('amended_charter', queryset=CharterAmendment.objects.order_by('date'))).order_by('-date')
    return render(request, 'charter.html', {'charter': charter})

def resolutions(request):
    amendments_prefetch = Prefetch('amended_resolution',queryset=ResolutionAmendment.objects.all().order_by('date'),to_attr='amendments')
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    resolutions = (Resolution.objects.prefetch_related('images', amendments_prefetch).all().order_by('-date'))
    return render(request, 'resolutions.html', {'resolutions': resolutions})

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

def treaties(request):
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    treaties = Treaty.objects.prefetch_related('images').all().order_by('-date')
    return render(request, 'treaties.html', {'treaties': treaties})

def executive_orders(request):
    executive_orders = ExecutiveOrder.objects.all().order_by('-charter', '-date')
    return render(request, 'executive_orders.html', {'executive_orders': executive_orders})

def alliances(request):
    # Prefetch images to avoid N+1 queries while maintaining date ordering
    alliances = Alliance.objects.prefetch_related('images').all().order_by('-date')
    return render(request, 'alliances.html', {'alliances': alliances})

def declaration_of_wars(request):
    declaration_of_wars = DeclarationOfWar.objects.all().order_by('-date')
    return render(request, 'declaration_of_wars.html', {'declaration_of_wars': declaration_of_wars})

def national_constitutions(request):
    national_constitutions = NationalConstitution.objects.prefetch_related(Prefetch('amended_national_constitution', queryset=NationalConstitutionAmendment.objects.order_by('date'))).order_by('nation', '-date')
    return render(request, 'national_constitutions.html', {'national_constitutions': national_constitutions})

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