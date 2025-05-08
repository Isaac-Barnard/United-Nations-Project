import csv
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from un_app.models import Building, Territory, Nation, Player

class Command(BaseCommand):
    help = 'Import buildings from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Fetch Territory and Nation (Owner) by their names
                    territory = Territory.objects.get(name=row['territory']) if row['territory'] else None
                    owner = Nation.objects.get(abbreviation=row['owner']) if row['owner'] else None

                    # Handle multiple main builders (comma-separated in CSV)
                    builders_list = row['main_builder'].split(',') if row['main_builder'] else []
                    main_builders = Player.objects.filter(username__in=[builder.strip() for builder in builders_list])

                    # Create the Building object
                    building = Building.objects.create(
                        name=row['name'],
                        territory=territory,  # Assign the fetched Territory object
                        owner=owner,  # Assign the fetched Nation object (Owner)
                        y_level_high_pt=row['y_level_high_pt'] or None, 
                        y_level_ground=row['y_level_ground'] or None,
                        year_completed=row['year_completed'] or None, 
                        completed=row['completed'] == 'TRUE', 
                        x_coordinate=row['x_coordinate'] or None,
                        z_coordinate=row['z_coordinate'] or None, 
                        historic_site=row['historic_site'] == 'TRUE',
                        architectural_genius=row['architectural_genius'] == 'TRUE',
                        mopq_award=row['mopq_award'] or None,
                        architectural_style=row['architectural_style'] or None ,
                        size=row['size']  or None,
                        materials=row['materials'],
                        furnished=row['furnished']  == 'TRUE'
                    )
                    # Add the main builders to the ManyToManyField
                    building.main_builders.add(*main_builders)

                    building.save()
                    self.stdout.write(self.style.SUCCESS(f"Added building: {building.name}"))

                except Territory.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Territory '{row['territory']}' does not exist."))
                except Nation.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: Owner Nation '{row['owner']}' does not exist."))
                except Player.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Error: One or more builders in '{row['main_builder']}' do not exist."))
                except IntegrityError as e:
                    if 'duplicate key value violates unique constraint' in str(e):
                        # Silently skip duplicates
                        pass
                    else:
                        self.stdout.write(self.style.ERROR(f"Error adding building: {row['name']} - {e}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error adding building: {row['name']} - {e}"))

        self.stdout.write(self.style.SUCCESS('CSV import completed!'))