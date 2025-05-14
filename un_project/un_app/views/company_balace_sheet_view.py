from django.shortcuts import render, get_object_or_404
from django.db.models import F, Value, Sum, DecimalField
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from ..models import Company, Denomination, Building, Item, ItemCount, LiquidAssetContainer, Liability, CompanyShareholder



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