from django.shortcuts import render, get_object_or_404
from un_app.models import Item, Denomination, ItemEvaluation  # ensure all are imported

def item_detail(request, image_name):
    item = get_object_or_404(Item, image_name=image_name)

    # Determine the image URL
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

    return render(request, 'item_detail.html', {
        'item': item,
        'image_url': image_url,
        'denominations': denominations,
        'evaluation_data': evaluation_data,
    })




def item_detail_selector(request):
    items = Item.objects.exclude(image_name='').order_by('name')  # only items with image_name
    return render(request, 'item_detail_selector.html', {
        'items': items,
    })