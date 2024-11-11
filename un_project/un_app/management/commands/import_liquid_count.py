import csv
from django.core.management.base import BaseCommand
from decimal import Decimal
from django.db import transaction
from un_app.models import LiquidAssetContainer, LiquidCount, Nation, Company, Denomination

class Command(BaseCommand):
    help = 'Import liquid counts from a CSV file'

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
                            self.stdout.write(self.style.ERROR(f"Error: Neither nation nor company provided for asset '{row['asset_name']}'"))
                            continue
                        if nation and company:
                            self.stdout.write(self.style.ERROR(f"Error: Both nation and company provided for asset '{row['asset_name']}'"))
                            continue

                        # Fetch the denomination by name; skip if it does not exist
                        try:
                            denomination = Denomination.objects.get(name=row['denomination'])
                        except Denomination.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f"Error: Denomination '{row['denomination']}' does not exist. Skipping asset '{row['asset_name']}'."))
                            continue

                        # Fetch or create the LiquidAssetContainer
                        container, _ = LiquidAssetContainer.objects.update_or_create(
                            name=row['asset_name'],
                            nation=nation,
                            company=company,
                            defaults={'ordering': 0}  # Set ordering as needed or use default
                        )

                        # Update or create the LiquidCount entry in the container
                        LiquidCount.objects.update_or_create(
                            asset_container=container,
                            denomination=denomination,
                            defaults={'count': Decimal(row['count'])}
                        )

                        self.stdout.write(self.style.SUCCESS(f"Processed asset '{row['asset_name']}' with count {row['count']} in {container}"))

                    except Nation.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error: Nation '{row['nation']}' does not exist."))
                    except Company.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error: Company '{row['company']}' does not exist."))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error adding liquid count for '{row['asset_name']}': {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import of liquid counts completed!'))
