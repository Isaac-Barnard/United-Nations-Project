from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Item, ItemCount, ItemEvaluation, ItemFixedPriceComponent, ItemEvaluationComponent

@receiver(post_save, sender=ItemCount)
@receiver(post_delete, sender=ItemCount)
def update_item_total_value(sender, instance, **kwargs):
    """Recalculate total_value for ItemCount when count changes."""
    item = instance.item
    total_value = sum(count.count * count.item.market_value for count in item.itemcount_set.all())
    instance.total_value = total_value
    instance.save()

@receiver(post_save, sender=Item)
@receiver(post_delete, sender=Item)
def update_item_counts_total_value_on_market_value_change(sender, instance, **kwargs):
    """Recalculate total_value in all related ItemCount instances when Item's market_value changes."""
    # Retrieve all ItemCount instances associated with the Item and update their total_value
    item_counts = instance.itemcount_set.all()
    for item_count in item_counts:
        item_count.total_value = item_count.count * instance.market_value
        # Use update to avoid triggering additional signals and recursion
        ItemCount.objects.filter(id=item_count.id).update(total_value=item_count.total_value)


@receiver(post_save, sender=ItemEvaluation)
@receiver(post_delete, sender=ItemEvaluation)
def update_item_market_value(sender, instance, **kwargs):
    """Recalculate market_value for market rate items when evaluations change."""
    item = instance.item
    if item.price_type == Item.MARKET_RATE:
        evaluations = item.item_evaluations.all()
        if evaluations.exists():
            item.market_value = item.market_price
            item.save()

@receiver(post_save, sender=ItemEvaluationComponent)
@receiver(post_delete, sender=ItemEvaluationComponent)
def update_item_market_value_on_evaluation_component_change(sender, instance, **kwargs):
    """Recalculate market_value for the associated Item when an ItemEvaluationComponent changes."""
    item_evaluation = instance.evaluation
    item = item_evaluation.item
    if item.price_type == Item.MARKET_RATE:
        # Trigger the update function for the item market value
        update_item_market_value(ItemEvaluation, item_evaluation)

@receiver(post_save, sender=ItemFixedPriceComponent)
@receiver(post_delete, sender=ItemFixedPriceComponent)
def update_item_fixed_price_value(sender, instance, **kwargs):
    """Recalculate market_value for fixed price items when price components change."""
    item = instance.item
    if item.price_type == Item.FIXED_PRICE:
        item.market_value = item.market_price
        item.save()