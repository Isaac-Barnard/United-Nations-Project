import csv
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from un_app.models import Building, Nation, Company, PartialBuildingOwnership
from un_app.signals_utils import disconnect_all_signals, reconnect_all_signals

class Command(BaseCommand):
    help = 'Import partial building ownerships from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Disconnect all signals before import
        disconnect_all_signals()

        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Fetch the building by name
                        building = Building.objects.get(name=row['building'])

                        # Determine the partial owner type (either Nation or Company)
                        if row['partial_owner_type'].lower() == 'nation':
                            content_type = ContentType.objects.get(model='nation')
                            owner_exists = Nation.objects.filter(abbreviation=row['partial_owner_abbreviation']).exists()
                        elif row['partial_owner_type'].lower() == 'company':
                            content_type = ContentType.objects.get(model='company')
                            owner_exists = Company.objects.filter(abbreviation=row['partial_owner_abbreviation']).exists()
                        else:
                            raise ValidationError(f"Invalid owner type: {row['partial_owner_type']}")

                        if not owner_exists:
                            raise ValidationError(f"{row['partial_owner_abbreviation']} is not a valid abbreviation.")


                        # Create or update PartialBuildingOwnership
                        partial_ownership, created = PartialBuildingOwnership.objects.update_or_create(
                            building=building,
                            partial_owner_type=content_type,
                            partial_owner_abbreviation=row['partial_owner_abbreviation'],
                            defaults={
                                'percentage': row['percentage']
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Added partial ownership: {row['partial_owner_abbreviation']} owns {row['percentage']}% of {building.name}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Updated partial ownership: {row['partial_owner_abbreviation']} owns {row['percentage']}% of {building.name}"))

                    except Building.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error: Building '{row['building']}' does not exist."))
                    except ValidationError as e:
                        self.stdout.write(self.style.ERROR(f"Validation Error: {e.message}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing row: {row} - {e}"))

            self.stdout.write(self.style.SUCCESS('CSV import for partial building ownerships completed!'))

        finally:
            # Reconnect all signals after import
            reconnect_all_signals()