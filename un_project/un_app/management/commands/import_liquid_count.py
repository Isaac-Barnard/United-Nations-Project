import csv
from django.core.management.base import BaseCommand
from un_app.models import LiquidCount, Nation, Company, Denomination

class Command(BaseCommand):
    help = 'Import liquid counts from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Fetch Nation or Company by their name
                    nation = Nation.objects.get(abbreviation=row['nation']) if row['nation'] else None
                    company = Company.objects.get(abbreviation=row['company']) if row['company'] else None

                    # Ensure that either nation or company is provided, but not both
                    if not (nation or company):
                        self.stdout.write(self.style.ERROR(f"Error: Neither nation nor company provided for asset '{row['asset_name']}'"))
                        continue
                    if nation and company:
                        self.stdout.write(self.style.ERROR(f"Error: Both nation and company provided for asset '{row['asset_name']}'"))
                        continue

                    # Fetch or create Denomination by its name
                    denomination, created = Denomination.objects.get_or_create(name=row['denomination'])

                    # Create or update the LiquidCount object
                    liquid_count, created = LiquidCount.objects.update_or_create(
                        asset_name=row['asset_name'],
                        nation=nation,
                        company=company,
                        denomination=denomination,
                        defaults={'count': row['count']}
                    )

                    action = "Added" if created else "Updated"
                    if action == "Added":
                        self.stdout.write(self.style.SUCCESS(f"{action} liquid count for asset '{liquid_count.asset_name}'"))
                    else:
                        self.stdout.write(self.style.WARNING(f"{action} liquid count for asset '{liquid_count.asset_name}'"))

                except Nation.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Nation '{row['nation']}' does not exist."))
                except Company.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Company '{row['company']}' does not exist."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error adding liquid count for '{row['asset_name']}': {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import of liquid counts completed!'))
