from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from django.db.models import Sum
from django.db import models
from .models import Item, ItemCount, ItemEvaluation, ItemFixedPriceComponent, ItemEvaluationComponent, Building, PartialBuildingOwnership, BuildingEvaluation, BuildingEvaluationComponent, Nation, LiquidCount, Company, LiquidAssetContainer, LiabilityPayment, Liability

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
    ownership_minus_partial = building.adjusted_ownership

    # Use update() to avoid triggering signals
    Building.objects.filter(pk=building.pk).update(ownership_minus_partial=ownership_minus_partial)


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
        # If the instance is a Building, use it directly
        building = instance
    elif isinstance(instance, PartialBuildingOwnership):
        # If it's a PartialBuildingOwnership, access the related Building
        building = instance.building
    elif isinstance(instance, BuildingEvaluation):
        # If it's a BuildingEvaluation, access the related Building
        building = instance.building
    elif isinstance(instance, BuildingEvaluationComponent):
        # If it's a BuildingEvaluationComponent, access the Building through evaluation
        building = instance.evaluation.building
    else:
        return  # Exit if none of the expected types

    # Calculate price_minus_partial using adjusted_ownership_price
    price_minus_partial = building.adjusted_ownership_price

    # Use update() to avoid triggering signals
    Building.objects.filter(pk=building.pk).update(price_minus_partial=price_minus_partial)


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
        partial_price = instance.partial_ownership_price()
        PartialBuildingOwnership.objects.filter(pk=instance.pk).update(partial_price=partial_price)

    elif isinstance(instance, Building):
        # Update partial_price for all related PartialBuildingOwnership entries
        partial_ownerships = instance.partialbuildingownership_set.all()
        for partial_ownership in partial_ownerships:
            partial_price = partial_ownership.partial_ownership_price()
            PartialBuildingOwnership.objects.filter(pk=partial_ownership.pk).update(partial_price=partial_price)

    elif isinstance(instance, BuildingEvaluation):
        # Get the building directly from the evaluation
        building = instance.building
        # Update all related PartialBuildingOwnership entries
        partial_ownerships = building.partialbuildingownership_set.all()
        for partial_ownership in partial_ownerships:
            partial_price = partial_ownership.partial_ownership_price()
            PartialBuildingOwnership.objects.filter(pk=partial_ownership.pk).update(partial_price=partial_price)

    elif isinstance(instance, BuildingEvaluationComponent):
        # Access the building through the evaluation on the BuildingEvaluationComponent
        building = instance.evaluation.building
        # Update all related PartialBuildingOwnership entries
        partial_ownerships = building.partialbuildingownership_set.all()
        for partial_ownership in partial_ownerships:
            partial_price = partial_ownership.partial_ownership_price()
            PartialBuildingOwnership.objects.filter(pk=partial_ownership.pk).update(partial_price=partial_price)

# --------------------------------------------------------------------
#                             Items
# --------------------------------------------------------------------

@receiver(post_save, sender=ItemCount)
@receiver(post_delete, sender=ItemCount)
def update_item_total_value(sender, instance, **kwargs):
    """Recalculate total_value for ItemCount when count changes."""
    total_value = instance.count * instance.item.market_value
    # Use update to avoid triggering signals
    ItemCount.objects.filter(pk=instance.pk).update(total_value=total_value)
    

@receiver(post_save, sender=Item)
@receiver(post_delete, sender=Item)
@receiver(post_save, sender=ItemFixedPriceComponent)
@receiver(post_delete, sender=ItemFixedPriceComponent)
@receiver(post_save, sender=ItemEvaluationComponent)
@receiver(post_delete, sender=ItemEvaluationComponent)
def update_item_counts_on_price_component_change(sender, instance, **kwargs):
    """
    Recalculate total_value in all related ItemCount instances when a price component changes.
    This affects both the direct item and any items that reference this item in their components.
    """
    # Get the directly related item
    item = instance.item
    
    # First update ItemCounts for the direct item
    item_counts = ItemCount.objects.filter(item=item)
    if item.price_type == Item.FIXED_PRICE:
        new_value = item.total_diamond_value
    elif item.price_type == Item.MARKET_RATE:
        new_value = item.market_price
    else:  # SECTION_DIVIDER
        new_value = Decimal('0')

    for item_count in item_counts:
        total_value = item_count.count * new_value
        ItemCount.objects.filter(id=item_count.id).update(total_value=total_value)

    # Then find and update any items that reference this item in their components
    referencing_components = ItemFixedPriceComponent.objects.filter(referenced_item=item)
    for comp in referencing_components:
        referenced_item = comp.item
        referenced_item_counts = ItemCount.objects.filter(item=referenced_item)
        
        if referenced_item.price_type == Item.FIXED_PRICE:
            ref_new_value = referenced_item.total_diamond_value
        elif referenced_item.price_type == Item.MARKET_RATE:
            ref_new_value = referenced_item.market_price
        else:  # SECTION_DIVIDER
            ref_new_value = Decimal('0')

        for item_count in referenced_item_counts:
            total_value = item_count.count * ref_new_value
            ItemCount.objects.filter(id=item_count.id).update(total_value=total_value)


@receiver(post_save, sender=ItemEvaluation)
@receiver(post_delete, sender=ItemEvaluation)
def update_item_market_value(sender, instance, **kwargs):
    """Recalculate market_value for market rate items when evaluations change."""
    item = instance.item
    if item.price_type == Item.MARKET_RATE:
        evaluations = item.item_evaluations.all()
        if evaluations.exists():
            new_market_value = item.market_price
            # Use update to avoid recursion
            Item.objects.filter(pk=item.pk).update(market_value=new_market_value)

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
        new_market_value = item.market_price
        # Use update to avoid recursion
        Item.objects.filter(pk=item.pk).update(market_value=new_market_value)

# --------------------------------------------------------------------
#                             Nation
# --------------------------------------------------------------------

@receiver(post_save, sender=LiquidCount)
@receiver(post_delete, sender=LiquidCount)
def update_total_liquid_asset_value(sender, instance, **kwargs):
    container = instance.asset_container
    if container:
        nation = container.nation
        company = container.company
        if nation:
            total = nation.calculate_total_liquid_asset_value()
            Nation.objects.filter(pk=nation.pk).update(total_liquid_asset_value=total)
        elif company:
            total = company.calculate_total_liquid_asset_value()
            Company.objects.filter(pk=company.pk).update(total_liquid_asset_value=total)

@receiver(post_save, sender=LiquidAssetContainer)
@receiver(post_delete, sender=LiquidAssetContainer)
def update_total_liquid_asset_value_on_container_change(sender, instance, **kwargs):
    nation = instance.nation
    company = instance.company
    if nation:
        total = nation.calculate_total_liquid_asset_value()
        Nation.objects.filter(pk=nation.pk).update(total_liquid_asset_value=total)
    elif company:
        total = company.calculate_total_liquid_asset_value()
        Company.objects.filter(pk=company.pk).update(total_liquid_asset_value=total)


@receiver(post_save, sender=ItemCount)
@receiver(post_delete, sender=ItemCount)
def update_total_item_asset_value(sender, instance, **kwargs):
    nation = instance.nation
    company = instance.company
    if nation:
        total = nation.calculate_total_item_asset_value()
        Nation.objects.filter(pk=nation.pk).update(total_item_asset_value=total)
    elif company:
        total = company.calculate_total_item_asset_value()
        Company.objects.filter(pk=company.pk).update(total_item_asset_value=total)


def update_total_building_asset_value(building):
    nation_owner_ids_to_update = set()
    company_owner_ids_to_update = set()

    # For Nations, add the building's owner
    if building.owner_id:
        nation_owner_ids_to_update.add(building.owner_id)

    # Collect Nations and Companies with partial ownership
    partials = building.partialbuildingownership_set.all()

    for partial in partials:
        if partial.partial_owner_type.model == 'nation':
            try:
                nation = Nation.objects.get(abbreviation=partial.partial_owner_abbreviation)
                nation_owner_ids_to_update.add(nation.id)
            except Nation.DoesNotExist:
                pass
        elif partial.partial_owner_type.model == 'company':
            try:
                company = Company.objects.get(abbreviation=partial.partial_owner_abbreviation)
                company_owner_ids_to_update.add(company.id)
            except Company.DoesNotExist:
                pass

    # Update total_building_asset_value for Nations
    for nation_id in nation_owner_ids_to_update:
        nation = Nation.objects.get(pk=nation_id)
        total = nation.calculate_total_building_asset_value()
        Nation.objects.filter(pk=nation.pk).update(total_building_asset_value=total)

    # Update total_building_asset_value for Companies
    for company_id in company_owner_ids_to_update:
        company = Company.objects.get(pk=company_id)
        total = company.calculate_total_building_asset_value()
        Company.objects.filter(pk=company.pk).update(total_building_asset_value=total)


@receiver(post_save, sender=Building)
@receiver(post_delete, sender=Building)
def building_changed(sender, instance, **kwargs):
    update_total_building_asset_value(instance)

@receiver(post_save, sender=PartialBuildingOwnership)
@receiver(post_delete, sender=PartialBuildingOwnership)
def partial_ownership_changed(sender, instance, **kwargs):
    update_total_building_asset_value(instance.building)

@receiver(post_save, sender=BuildingEvaluation)
@receiver(post_delete, sender=BuildingEvaluation)
def building_evaluation_changed(sender, instance, **kwargs):
    update_total_building_asset_value(instance.building)

@receiver(post_save, sender=BuildingEvaluationComponent)
@receiver(post_delete, sender=BuildingEvaluationComponent)
def building_evaluation_component_changed(sender, instance, **kwargs):
    update_total_building_asset_value(instance.evaluation.building)


@receiver(post_save, sender=LiabilityPayment)
def update_liability_after_payment(sender, instance, **kwargs):
    """Update the liability's remaining value whenever a payment is created or modified"""
    liability = instance.liability
    total_payments = LiabilityPayment.objects.filter(liability=liability).aggregate(
        total=models.Sum('diamond_amount'))['total'] or Decimal('0')
    
    liability.remaining_diamond_value = liability.total_diamond_value - total_payments
    liability.save()

@receiver(post_delete, sender=LiabilityPayment)
def update_liability_after_payment_delete(sender, instance, **kwargs):
    """Update the liability's remaining value whenever a payment is deleted"""
    liability = instance.liability
    total_payments = LiabilityPayment.objects.filter(liability=liability).aggregate(
        total=models.Sum('diamond_amount'))['total'] or Decimal('0')
    
    liability.remaining_diamond_value = liability.total_diamond_value - total_payments
    liability.save()