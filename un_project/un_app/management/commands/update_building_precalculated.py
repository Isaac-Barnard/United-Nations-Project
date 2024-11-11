from django.core.management.base import BaseCommand
from decimal import Decimal
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from un_app.models import Building, PartialBuildingOwnership

class Command(BaseCommand):
    help = 'Update ownership_minus_partial, price_minus_partial, and partial_price for buildings and partial ownerships'

    def handle(self, *args, **kwargs):
        updated_count = 0

        # Recalculate ownership_minus_partial and price_minus_partial for all buildings
        buildings_to_update = []
        for building in Building.objects.all():
            # Calculate ownership_minus_partial using adjusted_ownership property
            ownership_minus_partial = building.adjusted_ownership
            
            # Calculate price_minus_partial using adjusted_ownership_price property
            price_minus_partial = building.adjusted_ownership_price

            # Add the updated values to the list for bulk updating
            buildings_to_update.append((building.id, ownership_minus_partial, price_minus_partial))

        # Bulk update buildings using update query
        for building_id, ownership_minus_partial, price_minus_partial in buildings_to_update:
            Building.objects.filter(id=building_id).update(
                ownership_minus_partial=ownership_minus_partial,
                price_minus_partial=price_minus_partial
            )
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f'Updated Building with ID {building_id}'))

        # Recalculate partial_price for all PartialBuildingOwnership instances
        partial_ownerships_to_update = []
        for partial_ownership in PartialBuildingOwnership.objects.all():
            # Calculate partial_price using partial_ownership_price method
            partial_price = partial_ownership.partial_ownership_price()

            # Add the updated value to the list for bulk updating
            partial_ownerships_to_update.append((partial_ownership.id, partial_price))

        # Bulk update PartialBuildingOwnership partial_price
        for partial_ownership_id, partial_price in partial_ownerships_to_update:
            PartialBuildingOwnership.objects.filter(id=partial_ownership_id).update(partial_price=partial_price)
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f'Updated PartialBuildingOwnership with ID {partial_ownership_id}'))

        self.stdout.write(self.style.SUCCESS(f'Finished updating {updated_count} buildings and partial ownerships.'))