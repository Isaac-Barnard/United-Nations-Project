from django.shortcuts import render, get_object_or_404
from un_app.models import Item  # adjust import if needed

def item_detail(request, image_name):
    item = get_object_or_404(Item, image_name=image_name)
    # Image path relative to /static/
    image_url = f'images/minecraft_items/{item.image_name}.png' if item.image_name else None

    return render(request, 'item_detail.html', {
        'item': item,
        'image_url': image_url,
    })



def item_detail_selector(request):
    items = Item.objects.exclude(image_name='').order_by('name')  # only items with image_name
    return render(request, 'item_detail_selector.html', {
        'items': items,
    })