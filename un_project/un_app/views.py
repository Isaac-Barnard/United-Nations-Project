from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, FloatField, ExpressionWrapper, Count, Value, Sum, Window
from django.db.models.functions import Coalesce, Rank
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .forms import BuildingEvaluationForm, ItemEvaluationForm
from .models import Building, Player, Nation, PartialBuildingOwnership, BuildingEvaluation, BuildingEvaluationComponent, Denomination, UserProfile, ItemCount, ItemEvaluationComponent, ItemEvaluation, Item, Company, LiquidCount, LiquidAssetContainer, LiabilityPayment, Liability
from decimal import Decimal
from django.http import JsonResponse

def home(request):
    return render(request, 'home.html')


def building_list(request):
    # Annotate the queryset with the calculated height, handling null values
    buildings = Building.objects.select_related('owner', 'territory').annotate(
        # Use Coalesce to handle nulls, defaulting to 0
        calculated_height=ExpressionWrapper(
            Coalesce(F('y_level_high_pt'), Value(0)) - Coalesce(F('y_level_ground'), Value(0)),
            output_field=FloatField()
        ),
        # Add rank based on calculated height
        rank=Window(
            expression=Rank(),
            order_by=F('calculated_height').desc()
        )
    ).order_by('-calculated_height')

    return render(request, 'building_list.html', {'buildings': buildings})


def player_list(request):
    players = Player.objects.select_related('nation').annotate(
        num_buildings_built=Count('main_builds')
    ).order_by('-num_buildings_built')  # Sort by the number of buildings built in descending order
    return render(request, 'player_list.html', {'players': players})


def nation_balance_sheet(request, nation_abbreviation):
    # Get the nation by its abbreviation
    nation = get_object_or_404(Nation, abbreviation=nation_abbreviation)
    denominations = Denomination.objects.all()
    # Fetch all buildings owned by the nation
    buildings = Building.objects.filter(owner=nation)
    
    # Fetch buildings where the nation is a partial owner
    partial_buildings = Building.objects.filter(
        partialbuildingownership__partial_owner_abbreviation=nation.abbreviation
    ).annotate(
        ownership=F('partialbuildingownership__percentage'),
        partial_price=F('partialbuildingownership__partial_price')
    ).distinct()

    # Fetch all items and sort by the manual 'ordering' field
    all_items = Item.objects.all().order_by('ordering')  # Sorted by manual ordering
    items_with_count = ItemCount.objects.filter(nation=nation)

    # Create a dictionary to store count and total_values for each item
    item_count_dict = {
        item_count.item_id: (item_count.count, item_count.total_value) 
        for item_count in items_with_count
    }

    # Fetch and sort liquid asset containers by ordering
    liquid_containers = LiquidAssetContainer.objects.filter(nation=nation).order_by('ordering')
    liquid_asset_data = []

    # Loop through each container to retrieve LiquidCounts and calculate values
    for container in liquid_containers:
        container_total_in_diamonds = Decimal('0')
        container_counts = []

        # Calculate counts and diamond equivalents for each denomination
        for denomination in denominations:
            count_entry = container.liquidcount_set.filter(denomination=denomination).first()
            count_value = count_entry.count if count_entry else Decimal('0')
            container_counts.append(count_value)

            # Calculate diamond equivalent for this denomination
            container_total_in_diamonds += count_value * denomination.diamond_equivalent

        liquid_asset_data.append({
            'container_name': container.name,
            'counts': container_counts,
            'total_in_diamonds': container_total_in_diamonds,
        })


    # Calculate total value and market price for each item
    item_data = []
    for item in all_items:
        item_name = item.name if item.name else "Unnamed Item"
        market_value = item.market_value if item.market_value else Decimal('0')

        # Get the count and total_value for the item, defaulting to 0 if not present
        count, total_value = item_count_dict.get(item.id, (0, 0))

        item_data.append({
            'name': item_name,
            'market_value': market_value,
            'count': count,
            'total_value': total_value,
            'ordering': item.ordering,  # Ensure ordering is included for distribution
        })
    
    # Distribute items based on their 'ordering' value
    items_part1, items_part2, items_part3, items_part4, items_part5 = [], [], [], [], []
    for item in item_data:
        if 100 <= item['ordering'] < 200:
            items_part1.append(item)  # 100's range goes into items_part1
        elif 200 <= item['ordering'] < 300:
            items_part2.append(item)  # 200's range goes into items_part2
        elif 300 <= item['ordering'] < 400:
            items_part3.append(item)  # 300's range goes into items_part3
        elif 400 <= item['ordering'] < 500:
            items_part4.append(item)  # 400's range goes into items_part4
        elif 500 <= item['ordering'] < 600:
            items_part5.append(item)  # 500's range goes into items_part5

    # Fetch liabilities where this nation is the debtor
    nation_content_type = ContentType.objects.get_for_model(Nation)
    liabilities = Liability.objects.filter(
        debtor_type=nation_content_type,
        debtor_abbreviation=nation_abbreviation
    ).order_by('liability_type', 'creditor_abbreviation')

    # Calculate liability totals
    total_liabilities = liabilities.aggregate(
        total=Sum('total_diamond_value'))['total'] or Decimal('0')
    total_remaining_liabilities = liabilities.aggregate(
        total=Sum('remaining_diamond_value'))['total'] or Decimal('0')
            
    return render(request, 'nation_balance_sheet.html', {
    'nation': nation,
    'buildings': buildings,
    'partial_buildings': partial_buildings,
    'items_parts': [items_part1, items_part2, items_part3, items_part4, items_part5],  # Pass as a single list
    'denominations': denominations,
    'liquid_asset_data': liquid_asset_data,
    'liabilities': liabilities,
    'total_liabilities': total_liabilities,
    'total_remaining_liabilities': total_remaining_liabilities,
})


def company_balance_sheet(request, company_abbreviation):
    # Get the company by its abbreviation
    company = get_object_or_404(Company, abbreviation=company_abbreviation)
    denominations = Denomination.objects.all()
    
    # Fetch all buildings owned by the company
    #buildings = Building.objects.filter(owner=company)
    
     # Fetch buildings where the nation is a partial owner
    partial_buildings = Building.objects.filter(
        partialbuildingownership__partial_owner_abbreviation=company.abbreviation
    ).annotate(
        ownership=F('partialbuildingownership__percentage')
    ).distinct()

    # Fetch all items and sort by the manual 'ordering' field
    all_items = Item.objects.all().order_by('ordering')  # Sorted by manual ordering
    items_with_count = ItemCount.objects.filter(company=company)

    # Create a dictionary to store count and total_values for each item
    item_count_dict = {
        item_count.item_id: (item_count.count, item_count.total_value) 
        for item_count in items_with_count
    }

    # Fetch and sort liquid asset containers by ordering
    liquid_containers = LiquidAssetContainer.objects.filter(company=company).order_by('ordering')
    liquid_asset_data = []

    # Loop through each container to retrieve LiquidCounts and calculate values
    for container in liquid_containers:
        container_total_in_diamonds = Decimal('0')
        container_counts = []

        # Calculate counts and diamond equivalents for each denomination
        for denomination in denominations:
            count_entry = container.liquidcount_set.filter(denomination=denomination).first()
            count_value = count_entry.count if count_entry else Decimal('0')
            container_counts.append(count_value)

            # Calculate diamond equivalent for this denomination
            container_total_in_diamonds += count_value * denomination.diamond_equivalent

        liquid_asset_data.append({
            'container_name': container.name,
            'counts': container_counts,
            'total_in_diamonds': container_total_in_diamonds,
        })

    # Calculate total value and market price for each item
    item_data = []
    for item in all_items:
        item_name = item.name if item.name else "Unnamed Item"
        market_value = item.market_value if item.market_value else Decimal('0')

        # Get the count and total_value for the item, defaulting to 0 if not present
        count, total_value = item_count_dict.get(item.id, (0, 0))

        item_data.append({
            'name': item_name,
            'market_value': market_value,
            'count': count,
            'total_value': total_value,
            'ordering': item.ordering,  # Ensure ordering is included for distribution
        })
    
    # Distribute items based on their 'ordering' value
    items_part1, items_part2, items_part3, items_part4, items_part5 = [], [], [], [], []
    for item in item_data:
        if 100 <= item['ordering'] < 200:
            items_part1.append(item)  # 100's range goes into items_part1
        elif 200 <= item['ordering'] < 300:
            items_part2.append(item)  # 200's range goes into items_part2
        elif 300 <= item['ordering'] < 400:
            items_part3.append(item)  # 300's range goes into items_part3
        elif 400 <= item['ordering'] < 500:
            items_part4.append(item)  # 400's range goes into items_part4
        elif 500 <= item['ordering'] < 600:
            items_part5.append(item)  # 500's range goes into items_part5

    
    # Fetch liabilities where this company is the debtor
    company_content_type = ContentType.objects.get_for_model(Company)
    liabilities = Liability.objects.filter(
        debtor_type=company_content_type,
        debtor_abbreviation=company_abbreviation
    ).order_by('liability_type', 'creditor_abbreviation')

    # Calculate liability totals
    total_liabilities = liabilities.aggregate(
        total=Sum('total_diamond_value'))['total'] or Decimal('0')
    total_remaining_liabilities = liabilities.aggregate(
        total=Sum('remaining_diamond_value'))['total'] or Decimal('0')
    
            
    return render(request, 'company_balance_sheet.html', {
        'company': company,
        #'buildings': buildings,
        'partial_buildings': partial_buildings,
        'items_parts': [items_part1, items_part2, items_part3, items_part4, items_part5],  # Pass as a single list
        'denominations': denominations,
        'liquid_asset_data': liquid_asset_data,
        'liabilities': liabilities,
        'total_liabilities': total_liabilities,
        'total_remaining_liabilities': total_remaining_liabilities,
    })

def calculate_total_diamond_value(form_data, denominations):
    """Helper function to calculate total diamond value"""
    total_diamond_value = 0
    for denomination in denominations:
        field_name = f'denomination_{denomination.id}'
        quantity = form_data.get(field_name, 0)
        if isinstance(quantity, str):
            try:
                quantity = float(quantity)
            except ValueError:
                quantity = 0
        total_diamond_value += quantity * denomination.diamond_equivalent
    return total_diamond_value

@login_required
def evaluate_buildings(request):
    # Fetch the denominations to pass to the template
    denominations = Denomination.objects.all().order_by('priority')
    selected_building = None
    evaluation_data = []
    
    if request.method == 'POST':
        evaluation_form = BuildingEvaluationForm(request.POST)
        if evaluation_form.is_valid():

            selected_building = evaluation_form.cleaned_data['building']  # Get the selected building
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
            
            # Calculate total diamond value
            total_diamond_value = calculate_total_diamond_value(evaluation_form.cleaned_data, denominations)
            
            # Check if the evaluation is greater than 0
            if total_diamond_value <= 0:
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,
                    'error_message': 'The evaluation must be greater than 0.'
                })

            # Fetch existing evaluations for the selected building
            evaluations = BuildingEvaluation.objects.filter(building=selected_building).select_related('evaluator').prefetch_related('evaluation_components')

            for evaluation in evaluations:
                evaluator_name = evaluation.evaluator.username
                component_data = {denom.id: 0 for denom in denominations}  # Initialize all to 0
                
                for component in evaluation.evaluation_components.all():
                    component_data[component.denomination.id] = component.quantity  # Update with actual values

                evaluation_data.append({
                    'evaluator': evaluator_name,
                    'components': component_data
                })

            # Check if evaluator has already evaluated this building
            if BuildingEvaluation.objects.filter(building=selected_building, evaluator=evaluator_player).exists():
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,
                    'error_message': 'You have already evaluated this building.'
                })

            # Create BuildingEvaluation
            building_evaluation = BuildingEvaluation.objects.create(
                building=selected_building,
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
        'denominations': denominations,
        'selected_building': selected_building,
        'evaluation_data': evaluation_data,  # Pass evaluations to the template
    })

@login_required
def get_building_evaluations(request, building_id):
    denominations = Denomination.objects.all().order_by('priority')
    evaluations = BuildingEvaluation.objects.filter(building_id=building_id).select_related('evaluator').prefetch_related('evaluation_components')
    evaluation_data = []

    for evaluation in evaluations:
        evaluator_name = evaluation.evaluator.username
        component_data = {denom.name: 0 for denom in denominations}  # Initialize with denomination names

        for component in evaluation.evaluation_components.all():
            component_data[component.denomination.name] = float(component.quantity)  # Use denomination name

        evaluation_data.append({
            'evaluator': evaluator_name,
            'components': component_data,
            'total_diamond_value': float(evaluation.total_diamond_value)
        })

    return JsonResponse({
        'denominations': [denom.name for denom in denominations],
        'evaluation_data': evaluation_data
    })


def evaluation_success(request):
    return render(request, 'evaluation_success.html')


@login_required
def evaluate_items(request):
    denominations = Denomination.objects.all().order_by('priority')
    selected_item = None
    evaluation_data = []
    
    if request.method == 'POST':
        evaluation_form = ItemEvaluationForm(request.POST)
        if evaluation_form.is_valid():
            selected_item = evaluation_form.cleaned_data['item']
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
            
            # Calculate total diamond value
            total_diamond_value = calculate_total_diamond_value(evaluation_form.cleaned_data, denominations)
            
            # Check if the evaluation is greater than 0
            if total_diamond_value <= 0:
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,
                    'error_message': 'The evaluation must be greater than 0.'
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
            
            evaluations = ItemEvaluation.objects.filter(item=selected_item).select_related('evaluator').prefetch_related('evaluation_components')

            for evaluation in evaluations:
                evaluator_name = evaluation.evaluator.username
                component_data = {denom.id: 0 for denom in denominations}
                
                for component in evaluation.evaluation_components.all():
                    component_data[component.denomination.id] = component.quantity

                evaluation_data.append({
                    'evaluator': evaluator_name,
                    'components': component_data
                })

            if ItemEvaluation.objects.filter(item=selected_item, evaluator=evaluator_player).exists():
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,
                    'error_message': 'You have already evaluated this item.'
                })

            # Create ItemEvaluation
            item_evaluation = ItemEvaluation.objects.create(
                item=selected_item,
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
        'denominations': denominations,
        'selected_item': selected_item,
        'evaluation_data': evaluation_data,
    })

@login_required
def get_item_evaluations(request, item_id):
    denominations = Denomination.objects.all().order_by('priority')
    evaluations = ItemEvaluation.objects.filter(item_id=item_id).select_related('evaluator').prefetch_related('evaluation_components')
    evaluation_data = []

    for evaluation in evaluations:
        evaluator_name = evaluation.evaluator.username
        component_data = {denom.name: 0 for denom in denominations}

        for component in evaluation.evaluation_components.all():
            component_data[component.denomination.name] = float(component.quantity)

        evaluation_data.append({
            'evaluator': evaluator_name,
            'components': component_data,
            'total_diamond_value': float(evaluation.total_diamond_value)
        })

    return JsonResponse({
        'denominations': [denom.name for denom in denominations],
        'evaluation_data': evaluation_data
    })


def un_map(request):
    return render(request, 'un_map.html')