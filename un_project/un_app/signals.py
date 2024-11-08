from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Item, ItemCount, ItemEvaluation, ItemFixedPriceComponent, ItemEvaluationComponent, Building, PartialBuildingOwnership, BuildingEvaluation, BuildingEvaluationComponent

# --------------------------------------------------------------------
#                           Buildings
# --------------------------------------------------------------------

@receiver(post_save, sender=Building)
@receiver(post_save, sender=PartialBuildingOwnership)
@receiver(post_delete, sender=PartialBuildingOwnership)
def update_ownership_minus_partial(sender, instance, **kwargs):
    """Recalculate ownership_minus_partial whenever there is a change in Building or PartialBuildingOwnership."""
    if isinstance(instance, Building):
        building = instance
    else:
        building = instance.building

    # Calculate ownership_minus_partial using adjusted_ownership
    building.ownership_minus_partial = building.adjusted_ownership
    building.save(update_fields=['ownership_minus_partial'])


@receiver(post_save, sender=Building)
@receiver(post_save, sender=PartialBuildingOwnership)
@receiver(post_delete, sender=PartialBuildingOwnership)
@receiver(post_save, sender=BuildingEvaluation)
@receiver(post_delete, sender=BuildingEvaluation)
@receiver(post_save, sender=BuildingEvaluationComponent)
@receiver(post_delete, sender=BuildingEvaluationComponent)
def update_price_minus_partial(sender, instance, **kwargs):
    """Recalculate price_minus_partial whenever there is a relevant change in Building, PartialBuildingOwnership, BuildingEvaluation, or BuildingEvaluationComponent."""
    
    if isinstance(instance, Building):
        building = instance
    elif isinstance(instance, (PartialBuildingOwnership, BuildingEvaluation, BuildingEvaluationComponent)):
        building = instance.building

    # Calculate price_minus_partial using adjusted_ownership_price
    building.price_minus_partial = building.adjusted_ownership_price
    building.save(update_fields=['price_minus_partial'])


@receiver(post_save, sender=Building)
@receiver(post_save, sender=PartialBuildingOwnership)
@receiver(post_delete, sender=PartialBuildingOwnership)
@receiver(post_save, sender=BuildingEvaluation)
@receiver(post_delete, sender=BuildingEvaluation)
@receiver(post_save, sender=BuildingEvaluationComponent)
@receiver(post_delete, sender=BuildingEvaluationComponent)
def update_partial_price(sender, instance, **kwargs):
    """Recalculate partial_price in PartialBuildingOwnership whenever there is a relevant change in related models."""
    
    if isinstance(instance, PartialBuildingOwnership):
        # Recalculate partial_price for the current PartialBuildingOwnership instance
        instance.partial_price = instance.partial_ownership_price()
        instance.save(update_fields=['partial_price'])
    
    elif isinstance(instance, Building):
        # Update partial_price for all related PartialBuildingOwnership entries
        for partial_ownership in instance.partialbuildingownership_set.all():
            partial_ownership.partial_price = partial_ownership.partial_ownership_price()
            partial_ownership.save(update_fields=['partial_price'])
    
    elif isinstance(instance, (BuildingEvaluation, BuildingEvaluationComponent)):
        # Get the building and update all related PartialBuildingOwnership entries
        building = instance.building
        for partial_ownership in building.partialbuildingownership_set.all():
            partial_ownership.partial_price = partial_ownership.partial_ownership_price()
            partial_ownership.save(update_fields=['partial_price'])

# --------------------------------------------------------------------
#                             Items
# --------------------------------------------------------------------

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