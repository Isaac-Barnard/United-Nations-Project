from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, FloatField, ExpressionWrapper, Count, Value, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from .forms import BuildingEvaluationForm
from .models import Building, Player, Nation, PartialBuildingOwnership, BuildingEvaluation, BuildingEvaluationComponent, Denomination, UserProfile
from decimal import Decimal

def home(request):
    return render(request, 'home.html')


def building_list(request):
    # Annotate the queryset with the calculated height, handling null values
    buildings = Building.objects.select_related('owner', 'territory').annotate(
        # Use Coalesce to handle nulls, defaulting to 0
        calculated_height=ExpressionWrapper(
            Coalesce(F('y_level_high_pt'), Value(0)) - Coalesce(F('y_level_ground'), Value(0)),
            output_field=FloatField()
        )
    ).order_by('-calculated_height')  # Sort by calculated height

    return render(request, 'building_list.html', {'buildings': buildings})


def player_list(request):
    players = Player.objects.select_related('nation').annotate(
        num_buildings_built=Count('main_builds')
    ).order_by('-num_buildings_built')  # Sort by the number of buildings built in descending order
    return render(request, 'player_list.html', {'players': players})


def nation_balance_sheet(request, nation_abbreviation):
    # Get the nation by its abbreviation
    nation = get_object_or_404(Nation, abbreviation=nation_abbreviation)
    
    # Fetch all buildings owned by the nation (no need to annotate height or ownership here)
    buildings = Building.objects.filter(owner=nation)

    return render(request, 'nation_balance_sheet.html', {'nation': nation, 'buildings': buildings})


@login_required
def evaluate_buildings(request):
    if request.method == 'POST':
        evaluation_form = BuildingEvaluationForm(request.POST)
        if evaluation_form.is_valid():
            evaluator = request.user

            # Check if evaluator has a related UserProfile and Player instance
            try:
                evaluator_profile = evaluator.userprofile  # Access UserProfile related to User
                evaluator_player = evaluator_profile.player  # Get the associated Player
            except UserProfile.DoesNotExist:
                # Handle case where UserProfile doesn't exist
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'error_message': 'Your account is not set up correctly.'
                })

            # Check if the evaluator is authorized (un_rep=True)
            if not evaluator_player.un_rep:
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'error_message': 'You do not have permission to evaluate buildings.'
                })

            # Get building
            building = evaluation_form.cleaned_data['building']

            # Check if evaluator has already evaluated this building
            if BuildingEvaluation.objects.filter(building=building, evaluator=evaluator_player).exists():
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'error_message': 'You have already evaluated this building.'
                })

            # Create BuildingEvaluation
            building_evaluation = BuildingEvaluation.objects.create(
                building=building,
                evaluator=evaluator_player
            )

            # Iterate over denomination fields and create BuildingEvaluationComponents
            denominations = Denomination.objects.all()
            for denomination in denominations:
                field_name = f'denomination_{denomination.id}'
                quantity = evaluation_form.cleaned_data.get(field_name, 0)
                if quantity > 0:
                    BuildingEvaluationComponent.objects.create(
                        evaluation=building_evaluation,
                        denomination=denomination,
                        quantity=quantity
                    )

            return redirect('evaluation_success')
    else:
        evaluation_form = BuildingEvaluationForm()

    return render(request, 'evaluate_buildings.html', {
        'evaluation_form': evaluation_form
    })

def evaluation_success(request):
    return render(request, 'evaluation_success.html')