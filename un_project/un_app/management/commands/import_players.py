import csv
from django.core.management.base import BaseCommand
from un_app.models import Nation, Player

class Command(BaseCommand):
    help = 'Import players from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Fetch the associated Nation by abbreviation
                    nation_abbreviation = row.get('nation')
                    nation = Nation.objects.get(abbreviation=nation_abbreviation) if nation_abbreviation else None

                    # Create or update the Player object
                    player, created = Player.objects.update_or_create(
                        username=row['username'],
                        defaults={
                            'nation': nation,
                            'un_rep': row['un_rep'] == 'TRUE',
                            'description': row['description'] or None
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added new player: {player.username}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Updated player: {player.username}"))

                except Nation.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Nation with abbreviation '{nation_abbreviation}' does not exist."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error adding/updating player: {row['username']} - {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import completed!'))
