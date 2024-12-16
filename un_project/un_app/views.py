from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, FloatField, ExpressionWrapper, Count, Value, Sum, Window, DecimalField
from django.db.models.functions import Coalesce, Rank
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .forms import BuildingEvaluationForm, ItemEvaluationForm, ItemCounterForm, LiquidAssetForm
from .models import Building, Player, Nation, PartialBuildingOwnership, BuildingEvaluation, BuildingEvaluationComponent, Denomination, UserProfile, ItemCount, ItemEvaluationComponent, ItemEvaluation, Item, Company, LiquidCount, LiquidAssetContainer, LiabilityPayment, Liability, CompanyShareholder
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from un_app.templatetags.custom_filters import custom_decimal_places

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
    
    # Fetch receivables (liabilities where this nation is the creditor)
    receivables = Liability.objects.filter(
        creditor_type=nation_content_type,
        creditor_abbreviation=nation_abbreviation
    ).order_by('liability_type', 'debtor_abbreviation')

    # Calculate receivables totals
    total_receivables = receivables.aggregate(
        total=Sum('remaining_diamond_value'))['total'] or Decimal('0')
    

    #fetch stock investments
    nation_content_type = ContentType.objects.get_for_model(Nation)
    company_content_type = ContentType.objects.get_for_model(Company)
    stock_investments = CompanyShareholder.objects.filter(
        shareholder_type=nation_content_type,
        shareholder_abbreviation=nation_abbreviation
    ).select_related('company')

    # Calculate total value of investments
    total_investment_value = Decimal('0')
    for investment in stock_investments:
        company = investment.company
        
        # Get company's receivables
        company_receivables = Liability.objects.filter(
            creditor_type=company_content_type,
            creditor_abbreviation=company.abbreviation
        ).aggregate(
            total=Coalesce(
                Sum('remaining_diamond_value'),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total']

        # Get company's liabilities
        company_liabilities = Liability.objects.filter(
            debtor_type=company_content_type,
            debtor_abbreviation=company.abbreviation
        ).aggregate(
            total=Coalesce(
                Sum('remaining_diamond_value'),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total']

        company_value = (
            company.total_liquid_asset_value + 
            company.total_item_asset_value + 
            company.total_building_asset_value +
            company_receivables -
            company_liabilities
        )
        investment.value = (Decimal(str(investment.percentage)) * company_value) / Decimal('100')
        total_investment_value += investment.value

    
    # Calculate total assets
    total_assets = (
        nation.total_liquid_asset_value + 
        nation.total_item_asset_value + 
        nation.total_building_asset_value + 
        total_investment_value +
        total_receivables -
        total_remaining_liabilities
    )
    
            
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
    'receivables': receivables,
    'total_receivables': total_receivables,
    'stock_investments': stock_investments,
    'total_investment_value': total_investment_value,
    'total_assets': total_assets,
})


def company_balance_sheet(request, company_abbreviation):
    # Get the company by its abbreviation
    company = get_object_or_404(Company, abbreviation=company_abbreviation)
    denominations = Denomination.objects.all()
    
    # Fetch all buildings owned by the company
    #buildings = Building.objects.filter(owner=company)
    
     # Fetch buildings where the company is a partial owner
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
    
    # Fetch receivables (liabilities where this company is the creditor)
    receivables = Liability.objects.filter(
        creditor_type=company_content_type,
        creditor_abbreviation=company_abbreviation
    ).order_by('liability_type', 'debtor_abbreviation')

    # Calculate receivables totals
    total_receivables = receivables.aggregate(
        total=Sum('remaining_diamond_value'))['total'] or Decimal('0')

    # fetch stock investments
    company_content_type = ContentType.objects.get_for_model(Company)
    stock_investments = CompanyShareholder.objects.filter(
        shareholder_type=company_content_type,
        shareholder_abbreviation=company_abbreviation
    ).select_related('company')

    # Calculate total value of investments
    total_investment_value = Decimal('0')
    for investment in stock_investments:
        company = investment.company
        
        # Get company's receivables
        company_receivables = Liability.objects.filter(
            creditor_type=company_content_type,
            creditor_abbreviation=company.abbreviation
        ).aggregate(
            total=Coalesce(
                Sum('remaining_diamond_value'),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total']

        # Get company's liabilities
        company_liabilities = Liability.objects.filter(
            debtor_type=company_content_type,
            debtor_abbreviation=company.abbreviation
        ).aggregate(
            total=Coalesce(
                Sum('remaining_diamond_value'),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total']

        company_value = (
            company.total_liquid_asset_value + 
            company.total_item_asset_value + 
            company.total_building_asset_value +
            company_receivables -
            company_liabilities
        )
        investment.value = (Decimal(str(investment.percentage)) * company_value) / Decimal('100')
        total_investment_value += investment.value
    
    # Calculate total assets
    total_assets = (
        company.total_liquid_asset_value + 
        company.total_item_asset_value + 
        company.total_building_asset_value +
        total_investment_value +
        total_receivables -
        total_remaining_liabilities
    )
    
    # Fetch shareholders and calculate their share values
    shareholders = company.shareholders.all()
    # Calculate share values manually instead of using annotation
    for shareholder in shareholders:
        shareholder.share_value = (Decimal(str(shareholder.percentage)) * total_assets) / Decimal('100')

            
    return render(request, 'company_balance_sheet.html', {
        'company': company,
        #'buildings': buildings,
        'shareholders': shareholders,  # Now includes share_value
        'partial_buildings': partial_buildings,
        'items_parts': [items_part1, items_part2, items_part3, items_part4, items_part5],  # Pass as a single list
        'denominations': denominations,
        'liquid_asset_data': liquid_asset_data,
        'liabilities': liabilities,
        'total_liabilities': total_liabilities,
        'total_remaining_liabilities': total_remaining_liabilities,
        'receivables': receivables,
        'total_receivables': total_receivables,
        'stock_investments': stock_investments,
        'total_investment_value': total_investment_value,
        'total_assets': total_assets,
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



@login_required
def item_counter(request):
    selected_nation = None
    selected_company = None
    items_data = []
    liquid_asset_data = []
    items_parts = [[] for _ in range(5)]
    denominations = Denomination.objects.all().order_by('priority')
    owner = None
    
    # Handle POST requests
    if request.method == 'POST':
        form = ItemCounterForm(request.POST)
        if form.is_valid():
            nation = form.cleaned_data.get('nation')
            company = form.cleaned_data.get('company')
            item = form.cleaned_data.get('item')
            container = form.cleaned_data.get('container')
            count = form.cleaned_data.get('count')
            denomination = form.cleaned_data.get('denomination')

            owner = nation or company
            if owner:
                if item and count is not None:
                    if nation:
                        item_count, created = ItemCount.objects.get_or_create(
                            nation=nation,
                            item=item,
                            defaults={'count': 0}
                        )
                    else:
                        item_count, created = ItemCount.objects.get_or_create(
                            company=company,
                            item=item,
                            defaults={'count': 0}
                        )
                    item_count.count = count
                    item_count.save()

                if container and denomination and count is not None:
                    liquid_count, created = LiquidCount.objects.get_or_create(
                        asset_container=container,
                        denomination=denomination,
                        defaults={'count': 0}
                    )
                    liquid_count.count = count
                    liquid_count.save()

            return redirect('item_counter')

    # Handle GET requests
    else:
        if 'nation' in request.GET:
            try:
                selected_nation = get_object_or_404(Nation, id=request.GET['nation'])
                owner = selected_nation
                form = ItemCounterForm(initial={'nation': selected_nation})
            except:
                form = ItemCounterForm()
        elif 'company' in request.GET:
            try:
                selected_company = get_object_or_404(Company, id=request.GET['company'])
                owner = selected_company
                form = ItemCounterForm(initial={'company': selected_company})
            except:
                form = ItemCounterForm()
        else:
            form = ItemCounterForm()

    # Process items and liquid assets if we have an owner
    if owner:
        # Process items
        all_items = Item.objects.all().order_by('ordering')
        items_with_count = ItemCount.objects.filter(
            nation=owner if isinstance(owner, Nation) else None,
            company=owner if isinstance(owner, Company) else None
        )

        item_count_dict = {
            item_count.item_id: (item_count.count, item_count.total_value) 
            for item_count in items_with_count
        }

        for item in all_items:
            count, total_value = item_count_dict.get(item.id, (0, 0))
            items_data.append({
                'name': item.name,
                'market_value': item.market_value,
                'count': count,
                'total_value': total_value,
                'ordering': item.ordering,
            })

        # Process liquid assets
        liquid_containers = LiquidAssetContainer.objects.filter(
            nation=owner if isinstance(owner, Nation) else None,
            company=owner if isinstance(owner, Company) else None
        ).order_by('ordering')

        for container in liquid_containers:
            container_total_in_diamonds = Decimal('0')
            container_counts = []

            for denomination in denominations:
                count_entry = container.liquidcount_set.filter(
                    denomination=denomination).first()
                count_value = count_entry.count if count_entry else Decimal('0')
                container_counts.append(count_value)
                container_total_in_diamonds += count_value * denomination.diamond_equivalent

            liquid_asset_data.append({
                'container_name': container.name,
                'counts': container_counts,
                'total_in_diamonds': container_total_in_diamonds,
            })

        # Distribute items into parts
        for item in items_data:
            idx = (item['ordering'] // 100) - 1
            if 0 <= idx < 5:
                items_parts[idx].append(item)

    # Add the liquid asset form
    liquid_asset_form = LiquidAssetForm(denominations=denominations)
    
    return render(request, 'item_counter.html', {
        'form': form,
        'liquid_asset_form': liquid_asset_form,
        'selected_nation': selected_nation,
        'selected_company': selected_company,
        'items_parts': items_parts,
        'denominations': denominations,
        'liquid_asset_data': liquid_asset_data,
    })

@login_required
def get_containers(request):
    nation_id = request.GET.get('nation_id')
    company_id = request.GET.get('company_id')
    
    if nation_id:
        containers = LiquidAssetContainer.objects.filter(
            nation_id=nation_id
        ).values('id', 'name').order_by('ordering')
    elif company_id:
        containers = LiquidAssetContainer.objects.filter(
            company_id=company_id
        ).values('id', 'name').order_by('ordering')
    else:
        containers = []
        
    return JsonResponse({'containers': list(containers)})


def handle_liquid_asset_update(request):
    if not request.method == 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    try:
        data = request.POST
        container_name = data.get('container')
        denomination_id = data.get('denomination_id')
        count = data.get('count', '0')
        
        # Convert count to Decimal and validate
        try:
            count_decimal = Decimal(str(count))
            if count_decimal == Decimal('0'):
                return JsonResponse({'status': 'ignored', 'message': 'Zero value ignored'})
        except (ValueError, TypeError, InvalidOperation):
            return JsonResponse({'status': 'error', 'message': 'Invalid count value'})
        
        # Get the nation or company from the selected entity
        nation_id = data.get('nation_id')
        company_id = data.get('company_id')
        
        owner = None
        # Get the container based on nation/company
        if nation_id:
            nation = Nation.objects.get(id=nation_id)
            owner = nation
            container = LiquidAssetContainer.objects.get(nation=nation, name=container_name)
        elif company_id:
            company = Company.objects.get(id=company_id)
            owner = company
            container = LiquidAssetContainer.objects.get(company=company, name=container_name)
        else:
            return JsonResponse({'status': 'error', 'message': 'No nation or company selected'})
        
        # Get denomination
        denomination = Denomination.objects.get(id=denomination_id)
        
        # Update or create the liquid count
        liquid_count, created = LiquidCount.objects.update_or_create(
            asset_container=container,
            denomination=denomination,
            defaults={'count': count_decimal}
        )
        
        # Calculate new total in diamonds for the container
        container_total = Decimal('0')
        for lc in container.liquidcount_set.all():
            container_total += lc.count * lc.denomination.diamond_equivalent
        
        # Calculate new total for all liquid assets
        new_total_liquid = owner.calculate_total_liquid_asset_value()
        owner.total_liquid_asset_value = new_total_liquid
        owner.save()
        
        formatted_total = custom_decimal_places(container_total)
        formatted_count = format(liquid_count.count, 'g')
        formatted_total_liquid = custom_decimal_places(new_total_liquid)
        
        return JsonResponse({
            'status': 'success',
            'new_total_diamonds': formatted_total,
            'new_count': formatted_count,
            'total_liquid_value': formatted_total_liquid
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    

def handle_item_update(request):
    if not request.method == 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    try:
        data = request.POST
        item_name = data.get('item_name')
        count = data.get('count', '0')
        
        # Convert count to Decimal and validate
        try:
            count_decimal = Decimal(str(count))
            if count_decimal == Decimal('0'):
                return JsonResponse({'status': 'ignored', 'message': 'Zero value ignored'})
        except (ValueError, TypeError, InvalidOperation):
            return JsonResponse({'status': 'error', 'message': 'Invalid count value'})
        
        # Get the nation or company from the selected entity
        nation_id = data.get('nation_id')
        company_id = data.get('company_id')
        
        if not item_name:
            return JsonResponse({'status': 'error', 'message': 'Missing item name'})
            
        # Get the item
        item = Item.objects.get(name=item_name)
        
        if item.price_type == 'section_divider':
            return JsonResponse({'status': 'error', 'message': 'Cannot update section divider'})
        
        owner = None
        if nation_id:
            nation = Nation.objects.get(id=nation_id)
            owner = nation
            item_count, created = ItemCount.objects.update_or_create(
                nation=nation,
                item=item,
                defaults={'count': count_decimal}
            )
        elif company_id:
            company = Company.objects.get(id=company_id)
            owner = company
            item_count, created = ItemCount.objects.update_or_create(
                company=company,
                item=item,
                defaults={'count': count_decimal}
            )
        else:
            return JsonResponse({'status': 'error', 'message': 'No nation or company selected'})

        # Calculate the new total value for this item
        if item.price_type == 'fixed_price':
            new_total = count_decimal * item.total_diamond_value
        else:  # market_rate
            new_total = count_decimal * item.market_value
            
        # Update the total value and save
        item_count.total_value = new_total
        item_count.save()
        
        # Calculate new total for all items
        new_total_items = owner.calculate_total_item_asset_value()
        owner.total_item_asset_value = new_total_items
        owner.save()
        
        # Format the values using the custom filter
        formatted_total = custom_decimal_places(item_count.total_value)
        formatted_count = format(item_count.count, 'g')
        formatted_total_items = custom_decimal_places(new_total_items)
        
        return JsonResponse({
            'status': 'success',
            'new_total_value': formatted_total,
            'new_count': formatted_count,
            'total_items_value': formatted_total_items
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})