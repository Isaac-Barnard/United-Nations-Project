import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from un_app.models import ItemCount, Item, Nation, Company

class Command(BaseCommand):
    help = 'Import item counts from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Fetch Item by its name
                    item = Item.objects.get(name=row['item'])

                    # Fetch Nation or Company by abbreviation
                    nation = Nation.objects.get(abbreviation=row['nation']) if row['nation'] else None
                    company = Company.objects.get(abbreviation=row['company']) if row['company'] else None

                    # Ensure that only one of nation or company is provided
                    if not (nation or company):
                        self.stdout.write(self.style.ERROR(f"Error: Neither nation nor company provided for item '{row['item']}'"))
                        continue
                    if nation and company:
                        self.stdout.write(self.style.ERROR(f"Error: Both nation and company provided for item '{row['item']}'"))
                        continue

                    # Convert the count to Decimal
                    count_value = Decimal(row['count'])

                    # Create or update the ItemCount object
                    item_count, created = ItemCount.objects.update_or_create(
                        item=item,
                        nation=nation,
                        company=company,
                        defaults={'count': count_value}
                    )

                    action = "Added" if created else "Updated"
                    if action == "Added":
                        self.stdout.write(self.style.SUCCESS(f"{action} item count: {item_count}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"{action} item count: {item_count}"))

                except Item.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Item '{row['item']}' does not exist."))
                except Nation.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Nation '{row['nation']}' does not exist."))
                except Company.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Company '{row['company']}' does not exist."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error adding item count for '{row['item']}': {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import of item counts completed!'))