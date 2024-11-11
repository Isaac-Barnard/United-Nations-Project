from django.db.models.signals import post_save, post_delete
from un_app.models import (
    Building, PartialBuildingOwnership, BuildingEvaluation,
    BuildingEvaluationComponent, ItemCount, Item, ItemEvaluation,
    ItemEvaluationComponent, ItemFixedPriceComponent
)
from un_app.signals import (
    update_partial_price, update_ownership_minus_partial,
    update_price_minus_partial, update_item_total_value
)

def disconnect_all_signals():
    """Disconnect all relevant signals to avoid recursion during bulk import."""
    post_save.disconnect(update_ownership_minus_partial, sender=Building)
    post_save.disconnect(update_price_minus_partial, sender=PartialBuildingOwnership)
    post_delete.disconnect(update_price_minus_partial, sender=PartialBuildingOwnership)
    post_save.disconnect(update_partial_price, sender=BuildingEvaluation)
    post_delete.disconnect(update_partial_price, sender=BuildingEvaluation)
    post_save.disconnect(update_partial_price, sender=BuildingEvaluationComponent)
    post_delete.disconnect(update_partial_price, sender=BuildingEvaluationComponent)

    # Add Item-related signals
    post_save.disconnect(update_item_total_value, sender=ItemCount)
    post_delete.disconnect(update_item_total_value, sender=ItemCount)
    post_save.disconnect(update_item_total_value, sender=Item)
    post_delete.disconnect(update_item_total_value, sender=Item)
    post_save.disconnect(update_item_total_value, sender=ItemEvaluation)
    post_delete.disconnect(update_item_total_value, sender=ItemEvaluation)
    post_save.disconnect(update_item_total_value, sender=ItemEvaluationComponent)
    post_delete.disconnect(update_item_total_value, sender=ItemEvaluationComponent)
    post_save.disconnect(update_item_total_value, sender=ItemFixedPriceComponent)
    post_delete.disconnect(update_item_total_value, sender=ItemFixedPriceComponent)

def reconnect_all_signals():
    """Reconnect all relevant signals after bulk import is complete."""
    post_save.connect(update_ownership_minus_partial, sender=Building)
    post_save.connect(update_price_minus_partial, sender=PartialBuildingOwnership)
    post_delete.connect(update_price_minus_partial, sender=PartialBuildingOwnership)
    post_save.connect(update_partial_price, sender=BuildingEvaluation)
    post_delete.connect(update_partial_price, sender=BuildingEvaluation)
    post_save.connect(update_partial_price, sender=BuildingEvaluationComponent)
    post_delete.connect(update_partial_price, sender=BuildingEvaluationComponent)

    # Add Item-related signals
    post_save.connect(update_item_total_value, sender=ItemCount)
    post_delete.connect(update_item_total_value, sender=ItemCount)
    post_save.connect(update_item_total_value, sender=Item)
    post_delete.connect(update_item_total_value, sender=Item)
    post_save.connect(update_item_total_value, sender=ItemEvaluation)
    post_delete.connect(update_item_total_value, sender=ItemEvaluation)
    post_save.connect(update_item_total_value, sender=ItemEvaluationComponent)
    post_delete.connect(update_item_total_value, sender=ItemEvaluationComponent)
    post_save.connect(update_item_total_value, sender=ItemFixedPriceComponent)
    post_delete.connect(update_item_total_value, sender=ItemFixedPriceComponent)
