import csv
from django.core.management.base import BaseCommand
from un_app.models import Nation

class Command(BaseCommand):
    help = 'Import nations from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Create or update the Nation object
                    nation, created = Nation.objects.get_or_create(
                        name=row['name'],
                        abbreviation=row['abbreviation']
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added nation: {nation.name} ({nation.abbreviation})"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Nation '{nation.name}' already exists."))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error adding nation: {row['name']} - {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import completed!'))
