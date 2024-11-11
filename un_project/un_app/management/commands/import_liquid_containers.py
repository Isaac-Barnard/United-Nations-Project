import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from un_app.models import LiquidAssetContainer, Nation, Company

class Command(BaseCommand):
    help = 'Import ordering data for LiquidAssetContainers from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            with transaction.atomic():
                for row in reader:
                    try:
                        # Fetch Nation or Company by abbreviation
                        nation = Nation.objects.get(abbreviation=row['nation']) if row['nation'] else None
                        company = Company.objects.get(abbreviation=row['company']) if row['company'] else None

                        # Ensure either nation or company is set, but not both
                        if not (nation or company):
                            self.stdout.write(self.style.ERROR(f"Error: Neither nation nor company provided for container '{row['name']}'"))
                            continue
                        if nation and company:
                            self.stdout.write(self.style.ERROR(f"Error: Both nation and company provided for container '{row['name']}'"))
                            continue

                        # Fetch the LiquidAssetContainer by name, nation, and company
                        try:
                            container = LiquidAssetContainer.objects.get(
                                name=row['name'],
                                nation=nation,
                                company=company
                            )
                        except LiquidAssetContainer.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f"Error: LiquidAssetContainer '{row['name']}' does not exist for given nation/company."))
                            continue

                        # Update the ordering field
                        container.ordering = int(row['ordering'])
                        container.save(update_fields=['ordering'])

                        self.stdout.write(self.style.SUCCESS(f"Updated ordering for '{container.name}' to {container.ordering}"))

                    except Nation.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error: Nation '{row['nation']}' does not exist."))
                    except Company.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error: Company '{row['company']}' does not exist."))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error updating ordering for '{row['name']}': {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import of ordering data completed!'))
