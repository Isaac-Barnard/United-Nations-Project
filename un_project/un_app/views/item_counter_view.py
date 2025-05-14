from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..forms import ItemCounterForm, LiquidAssetForm
from ..models import Denomination, LiquidAssetContainer, ItemCount, LiquidCount, Nation, Company, Item
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from un_app.templatetags.custom_filters import custom_decimal_places

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