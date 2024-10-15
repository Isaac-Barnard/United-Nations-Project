from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, FloatField, ExpressionWrapper, Count, Value, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from .forms import BuildingEvaluationForm, ItemEvaluationForm
from .models import Building, Player, Nation, PartialBuildingOwnership, BuildingEvaluation, BuildingEvaluationComponent, Denomination, UserProfile, ItemCount, ItemEvaluationComponent, ItemEvaluation, Item
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

    # Fetch all items and sort by the manual 'ordering' field
    all_items = Item.objects.all().order_by('ordering')  # Sorted by manual ordering
    items_with_count = ItemCount.objects.filter(nation=nation)

    # Create a dictionary to store counts for each item
    item_count_dict = {item_count.item_id: item_count.count for item_count in items_with_count}

    # Calculate total value and market price for each item
    item_data = []
    for item in all_items:
        item_name = item.name if item.name else "Unnamed Item"
        market_price = item.market_price if item.market_price else Decimal('0')
        
        # Get the count for the item, defaulting to 0 if not present
        count = item_count_dict.get(item.id, 0)
        total_value = market_price * count

        item_data.append({
            'name': item_name,
            'market_price': market_price,
            'count': count,
            'total_value': total_value,
            'ordering': item.ordering,  # Ensure ordering is included for distribution
        })
    
    # Distribute items based on their 'ordering' value
    items_part1, items_part2, items_part3, items_part4 = [], [], [], []
    for item in item_data:
        if 100 <= item['ordering'] < 200:
            items_part1.append(item)  # 100's range goes into items_part1
        elif 200 <= item['ordering'] < 300:
            items_part2.append(item)  # 200's range goes into items_part2
        elif 300 <= item['ordering'] < 400:
            items_part3.append(item)  # 300's range goes into items_part3
        elif 400 <= item['ordering'] < 500:
            items_part4.append(item)  # 400's range goes into items_part4
            
    return render(request, 'nation_balance_sheet.html', {
        'nation': nation,
        'buildings': buildings,
        'partial_buildings': partial_buildings,
        'items_part1': items_part1,  # First set of items
        'items_part2': items_part2,  # Second set of items
        'items_part3': items_part3,  # Third set of items
        'items_part4': items_part4,  # Fourth set of items
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


@login_required
def evaluate_items(request):
    # Fetch the denominations to pass to the template
    denominations = Denomination.objects.all().order_by('priority')
    
    if request.method == 'POST':
        evaluation_form = ItemEvaluationForm(request.POST)
        if evaluation_form.is_valid():
            evaluator = request.user

            # Check if evaluator has a related UserProfile and Player instance
            try:
                evaluator_profile = evaluator.userprofile  # Access UserProfile related to User
                evaluator_player = evaluator_profile.player  # Get the associated Player
            except UserProfile.DoesNotExist:
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'Your account is not set up correctly.'
                })

            # Check if the evaluator is authorized (un_rep=True)
            if not evaluator_player.un_rep:
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'You do not have permission to evaluate items.'
                })

            # Get item
            item = evaluation_form.cleaned_data['item']

            # Check if evaluator has already evaluated this item
            if ItemEvaluation.objects.filter(item=item, evaluator=evaluator_player).exists():
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'You have already evaluated this item.'
                })

            # Create ItemEvaluation
            item_evaluation = ItemEvaluation.objects.create(
                item=item,
                evaluator=evaluator_player
            )

            # Iterate over denomination fields and create ItemEvaluationComponents
            for denomination in denominations:
                field_name = f'denomination_{denomination.id}'
                quantity = evaluation_form.cleaned_data.get(field_name, 0)
                if quantity > 0:
                    ItemEvaluationComponent.objects.create(
                        evaluation=item_evaluation,
                        denomination=denomination,
                        quantity=quantity
                    )

            return redirect('evaluation_success')

    else:
        evaluation_form = ItemEvaluationForm()

    # Always pass the denominations to the template
    return render(request, 'evaluate_items.html', {
        'evaluation_form': evaluation_form,
        'denominations': denominations  # Ensure denominations are passed on GET request
    })
