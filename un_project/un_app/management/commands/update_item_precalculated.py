from django.core.management.base import BaseCommand
from decimal import Decimal
from un_app.models import Item, ItemCount

class Command(BaseCommand):
    help = 'Update market_value and total_value for all items'

    def handle(self, *args, **kwargs):
        # Track the number of updated records
        updated_count = 0

        # Recalculate market_value for all fixed-price and market-rate items in bulk
        items_to_update = []
        for item in Item.objects.all():
            if item.price_type == Item.FIXED_PRICE:
                # Recalculate market_value for fixed-price items without triggering save() recursion
                market_value = item._total_diamond_value()
            elif item.price_type == Item.MARKET_RATE:
                # Calculate average market rate for market rate items
                evaluations = item.item_evaluations.all()
                if evaluations.exists():
                    total_value = sum(evaluation.total_diamond_value for evaluation in evaluations)
                    market_value = (total_value / evaluations.count()).quantize(Decimal('0.000001'))
                else:
                    market_value = Decimal('0')
            else:
                continue
            
            # Add the updated value to the list for bulk updating
            items_to_update.append((item.id, market_value))

        # Bulk update items using update query
        for item_id, market_value in items_to_update:
            Item.objects.filter(id=item_id).update(market_value=market_value)
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f'Updated item with ID {item_id}'))

        # Recalculate and bulk update total_value for ItemCount instances
        item_counts_to_update = []
        for item_count in ItemCount.objects.all():
            total_value = item_count.count * item_count.item.market_value
            item_counts_to_update.append((item_count.id, total_value))

        # Bulk update ItemCount total_value
        for item_count_id, total_value in item_counts_to_update:
            ItemCount.objects.filter(id=item_count_id).update(total_value=total_value)
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f'Updated item count with ID {item_count_id}'))

        self.stdout.write(self.style.SUCCESS(f'Finished updating {updated_count} items and item counts.'))
