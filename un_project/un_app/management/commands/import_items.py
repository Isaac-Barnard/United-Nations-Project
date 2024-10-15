import csv
from django.core.management.base import BaseCommand
from un_app.models import Item

class Command(BaseCommand):
    help = 'Import items from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Create the Item object
                    item = Item.objects.create(
                        name=row['name'],
                        price_type=row['price_type'].lower().replace(' ', '_'),  # Ensures price_type matches the choices format
                        description=row['description'] or '',  # Handles empty descriptions
                        ordering=int(row['ordering'])  # Ensures ordering is an integer
                    )

                    item.save()  # Save the item to the database
                    self.stdout.write(self.style.SUCCESS(f"Added item: {item.name}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error adding item: {row['name']} - {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import completed!'))
