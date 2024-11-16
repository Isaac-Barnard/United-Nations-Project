# management/commands/import_liabilities.py
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import datetime
import csv
from decimal import Decimal
from un_app.models import Liability

class Command(BaseCommand):
    help = 'Import liabilities from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be imported without actually importing',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']

        # Cache content types to avoid repeated database lookups
        nation_type = ContentType.objects.get(model='nation')
        company_type = ContentType.objects.get(model='company')

        def get_content_type(type_str):
            """Convert type string to ContentType"""
            if type_str.lower() == 'nation':
                return nation_type
            elif type_str.lower() == 'company':
                return company_type
            else:
                raise ValueError(f"Invalid type: {type_str}")

        def parse_date(date_str):
            """Parse date string into timezone-aware datetime object"""
            if not date_str:
                return None
            try:
                # Try different date formats
                formats = [
                    '%m/%d/%y',    # 2/2/22
                    '%m/%d/%Y',    # 2/2/2022
                    '%Y-%m-%d',    # 2022-02-02
                    '%d/%m/%y',    # 02/02/22
                    '%d/%m/%Y',    # 02/02/2022
                ]
                
                parsed_date = None
                for fmt in formats:
                    try:
                        parsed_date = datetime.strptime(date_str.strip(), fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date is None:
                    raise ValueError(f"Could not parse date: {date_str}")
                
                # Make the datetime timezone-aware using the default timezone
                return timezone.make_aware(
                    # Set time to beginning of day
                    datetime.combine(parsed_date.date(), datetime.min.time()),
                    timezone=timezone.get_default_timezone()
                )
            except Exception as e:
                raise ValueError(f"Error parsing date '{date_str}': {str(e)}")

        created_count = 0
        error_count = 0
        
        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                
                for row_number, row in enumerate(reader, start=2):  # Start at 2 to account for header row
                    try:
                        # Prepare liability data
                        liability_data = {
                            'debtor_type': get_content_type(row['debtor_type']),
                            'debtor_abbreviation': row['debtor_abbreviation'],
                            'creditor_type': get_content_type(row['creditor_type']),
                            'creditor_abbreviation': row['creditor_abbreviation'],
                            'liability_type': row['liability_type'],
                            'description': row['description'],
                            'creation_date': parse_date(row['creation_date']),
                            'due_date': parse_date(row['due_date']),
                            'total_diamond_value': Decimal(row['total_diamond_value']),
                        }

                        if dry_run:
                            self.stdout.write(f"Would create liability: {liability_data}")
                            created_count += 1
                            continue

                        # Create the liability
                        liability = Liability.objects.create(**liability_data)
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"Created liability: {liability}"
                        ))

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(
                            f"Error on row {row_number}: {str(e)}"
                        ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
            return

        # Print summary
        self.stdout.write("\nImport Summary:")
        self.stdout.write(f"{'Would create' if dry_run else 'Created'} {created_count} liabilities")
        if error_count:
            self.stdout.write(self.style.ERROR(f"Encountered {error_count} errors"))