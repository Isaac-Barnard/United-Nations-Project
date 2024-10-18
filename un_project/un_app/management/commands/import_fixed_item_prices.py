import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from un_app.models import Item, Denomination, ItemFixedPriceComponent

class Command(BaseCommand):
    help = 'Import item fixed price components from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Fetch the Item
                    item = Item.objects.get(name=row['item'])

                    # Get the denomination if provided
                    denomination = None
                    if row['denomination']:
                        denomination = Denomination.objects.get(name=row['denomination'])

                    # Get the quantity if provided
                    quantity = Decimal(row['quantity'].strip()) if row['quantity'] else None

                    # Get the referenced item if provided
                    referenced_item = None
                    if row['referenced_item']:
                        referenced_item = Item.objects.get(name=row['referenced_item'])

                    # Get the percentage of item if provided
                    percentage_of_item = Decimal(row['percentage_of_item'].strip()) if row['percentage_of_item'] else None

                    # Validate that either denomination or referenced_item is provided (not both or neither)
                    if not denomination and not referenced_item:
                        raise ValidationError("A price component must have either a denomination or a referenced item.")
                    if denomination and referenced_item:
                        raise ValidationError("A price component cannot have both a denomination and a referenced item.")
                    if referenced_item and not percentage_of_item:
                        raise ValidationError("When using a referenced item, a percentage of that item’s price must be specified.")

                    # Create or update the ItemFixedPriceComponent
                    component, created = ItemFixedPriceComponent.objects.get_or_create(
                        item=item,
                        denomination=denomination,
                        referenced_item=referenced_item,
                        defaults={'quantity': quantity, 'percentage_of_item': percentage_of_item}
                    )

                    if not created:
                        # Update existing component if it already exists
                        component.quantity = quantity
                        component.percentage_of_item = percentage_of_item
                        component.save()

                    self.stdout.write(self.style.SUCCESS(f"Added/Updated price component for item: {item.name}"))

                except Item.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Item '{row['item']}' does not exist."))
                except Denomination.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Denomination '{row['denomination']}' does not exist."))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Validation error for item '{row['item']}': {e.message}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing item '{row['item']}': {str(e)}"))

        self.stdout.write(self.style.SUCCESS('CSV import completed!'))
