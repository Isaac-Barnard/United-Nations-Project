import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from un_app.models import Building, Player, BuildingEvaluation, BuildingEvaluationComponent, Denomination

class Command(BaseCommand):
    help = 'Import building evaluations from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Map columns to denominations
        denomination_mapping = {
            'Netherite Ingots': 'Netherite Ingot',
            'Diamonds': 'Diamond',
            'Gold Ingots': 'Gold Ingot',
            'Emeralds': 'Emerald',
            'Iron Ingots': 'Iron Ingot',
            'Copper Ingots': 'Copper Ingot',
            'Redstone Dust': 'Redstone Dust',
            'Lapis Lazuli': 'Lapis Lazuli',
            'Coal': 'Coal'
        }

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['evaluator'].lower() == 'decoy':  # Skip if the evaluator is 'decoy'
                    self.stdout.write(self.style.WARNING(f"Skipping evaluation for building '{row['building']}' by evaluator 'decoy'"))
                    continue

                try:
                    # Fetch the Building and Player (evaluator)
                    building = Building.objects.get(name=row['building'])
                    evaluator = Player.objects.get(username=row['evaluator'])

                    # Create or get the BuildingEvaluation object
                    evaluation, created = BuildingEvaluation.objects.get_or_create(
                        building=building,
                        evaluator=evaluator
                    )

                    # Loop through each denomination and add components if they exist in the row
                    for column_name, denomination_name in denomination_mapping.items():
                        if row[column_name]:  # Check if there's a value in this column
                            quantity = Decimal(row[column_name].strip())
                            denomination = Denomination.objects.get(name=denomination_name)

                            # Create the BuildingEvaluationComponent object
                            BuildingEvaluationComponent.objects.create(
                                evaluation=evaluation,
                                denomination=denomination,
                                quantity=quantity
                            )

                    evaluation.save()
                    self.stdout.write(self.style.SUCCESS(f"Added evaluation for building: {building.name} by {evaluator.username}"))

                except Building.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Building '{row['building']}' does not exist."))
                except Player.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Evaluator '{row['evaluator']}' does not exist."))
                except Denomination.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Denomination '{denomination_name}' does not exist."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error adding evaluation: {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import completed!'))
