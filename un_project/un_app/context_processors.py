from .models import Nation, Company

def nations_and_companies(request):
    nations = Nation.objects.all()
    companies = Company.objects.all()
    return {
        'nations': nations,
        'companies': companies,
    }