from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from un_app.models import Item, Denomination, ItemEvaluation

def item_detail(request, image_name):
    item = get_object_or_404(Item, image_name=image_name)

    if item.special_image_name:
        image_url = f'images/minecraft_items/{item.special_image_name}.png'
    else:
        image_url = f'images/minecraft_items/{item.image_name}.png' if item.image_name else None

    # Fetch denominations and evaluations
    denominations = Denomination.objects.all().order_by('priority')
    evaluations = (
        ItemEvaluation.objects
        .filter(item=item)
        .select_related('evaluator')
        .prefetch_related('evaluation_components__denomination')
    )

    evaluation_data = []
    for evaluation in evaluations:
        evaluator_name = evaluation.evaluator.username
        total_diamond_value = getattr(evaluation, 'total_diamond_value', 0)
        component_data = {denom.id: 0 for denom in denominations}

        for component in evaluation.evaluation_components.all():
            component_data[component.denomination.id] = component.quantity

        evaluation_data.append({
            'evaluator': evaluator_name,
            'total_diamond_value': total_diamond_value,
            'components': component_data,
        })

    price_components = (
        item.price_components.select_related('denomination', 'referenced_item').all()
        if item.price_type == Item.FIXED_PRICE
        else None
    )

    # Separate and calculate subtotals
    item_components = []
    currency_components = []
    total_value = Decimal('0')

    if price_components:
        for c in price_components:
            if c.denomination:
                worth = Decimal(c.quantity) * Decimal(c.denomination.diamond_equivalent)
                total_value += worth
                item_components.append({
                    'name': c.denomination.name,
                    'quantity': c.quantity,
                    'worth': worth
                })
            elif c.referenced_item:
                # Calculate the worth of this referenced item
                referenced_price = c.referenced_item.market_price or Decimal('0')
                worth = (Decimal(c.percentage_of_item) / Decimal('100')) * referenced_price
                total_value += worth
                currency_components.append({
                    'name': c.referenced_item.name,
                    'percentage': c.percentage_of_item,
                    'referenced_price': referenced_price,
                    'worth': worth
                })

    return render(request, 'item_detail.html', {
        'item': item,
        'image_url': image_url,
        'denominations': denominations,
        'evaluation_data': evaluation_data,
        'item_components': item_components,
        'currency_components': currency_components,
        'total_value': total_value,
    })





def item_detail_selector(request):
    items = Item.objects.exclude(image_name='').order_by('name')  # only items with image_name
    return render(request, 'item_detail_selector.html', {
        'items': items,
    })