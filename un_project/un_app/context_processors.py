from .models import Nation

def nations(request):
    """
    A context processor to add the list of nations to all templates.
    """
    return {
        'nations': Nation.objects.all()
    }