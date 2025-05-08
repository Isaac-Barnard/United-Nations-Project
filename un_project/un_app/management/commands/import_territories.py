import csv
from django.core.management.base import BaseCommand
from un_app.models import Territory

class Command(BaseCommand):
    help = 'Import territories from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Create or update the Territory object
                    territory, created = Territory.objects.get_or_create(
                        name=row['name']
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added territory: {territory.name}"))
                    #else:
                        #self.stdout.write(self.style.WARNING(f"Territory '{territory.name}' already exists."))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error adding territory: {row['name']} - {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import completed!'))
