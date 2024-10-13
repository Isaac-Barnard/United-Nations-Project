from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, FloatField, ExpressionWrapper, Count, Value, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from .forms import BuildingEvaluationForm
from .models import Building, Player, Nation, PartialBuildingOwnership, BuildingEvaluation, BuildingEvaluationComponent, Denomination, UserProfile, ItemCount
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
    
    # Fetch all buildings owned by the nation
    buildings = Building.objects.filter(owner=nation)
    
    # Fetch buildings where the nation is a partial owner
    partial_buildings = Building.objects.filter(
        partialbuildingownership__partial_owner_abbreviation=nation.abbreviation
    ).annotate(
        ownership=F('partialbuildingownership__percentage')
    ).distinct()

    # Fetch item counts for the nation
    items_with_count = ItemCount.objects.filter(nation=nation)

    # Calculate total value and market price for each item
    item_data = []
    for item_count in items_with_count:
        item = item_count.item

        # Check and log values for debugging
        item_name = item.name if item.name else "Unnamed Item"
        market_price = item.market_price if item.market_price else Decimal('0')

        total_value = market_price * item_count.count

        item_data.append({
            'name': item_name,
            'market_price': market_price,
            'count': item_count.count,
            'total_value': total_value,
        })
    
    # Distribute items into four parts (round-robin)
    items_part1, items_part2, items_part3, items_part4 = [], [], [], []
    for index, item in enumerate(item_data):
        if index % 4 == 0:
            items_part1.append(item)
        elif index % 4 == 1:
            items_part2.append(item)
        elif index % 4 == 2:
            items_part3.append(item)
        else:
            items_part4.append(item)
            

    return render(request, 'nation_balance_sheet.html', {
        'nation': nation,
        'buildings': buildings,
        'partial_buildings': partial_buildings,
        'items_part1': items_part1,  # First third of items
        'items_part2': items_part2,  # Second third of items
        'items_part3': items_part3,  # Final third of items
        'items_part4': items_part4,  # Fourth quarter of items
    })



@login_required
def evaluate_buildings(request):
    # Fetch the denominations to pass to the template
    denominations = Denomination.objects.all().order_by('priority')
    
    if request.method == 'POST':
        evaluation_form = BuildingEvaluationForm(request.POST)
        if evaluation_form.is_valid():
            evaluator = request.user

            # Check if evaluator has a related UserProfile and Player instance
            try:
                evaluator_profile = evaluator.userprofile  # Access UserProfile related to User
                evaluator_player = evaluator_profile.player  # Get the associated Player
            except UserProfile.DoesNotExist:
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'Your account is not set up correctly.'
                })

            # Check if the evaluator is authorized (un_rep=True)
            if not evaluator_player.un_rep:
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'You do not have permission to evaluate buildings.'
                })

            # Get building
            building = evaluation_form.cleaned_data['building']

            # Check if evaluator has already evaluated this building
            if BuildingEvaluation.objects.filter(building=building, evaluator=evaluator_player).exists():
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'You have already evaluated this building.'
                })

            # Create BuildingEvaluation
            building_evaluation = BuildingEvaluation.objects.create(
                building=building,
                evaluator=evaluator_player
            )

            # Iterate over denomination fields and create BuildingEvaluationComponents
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

    # Always pass the denominations to the template
    return render(request, 'evaluate_buildings.html', {
        'evaluation_form': evaluation_form,
        'denominations': denominations  # Ensure denominations are passed on GET request
    })


def evaluation_success(request):
    return render(request, 'evaluation_success.html')