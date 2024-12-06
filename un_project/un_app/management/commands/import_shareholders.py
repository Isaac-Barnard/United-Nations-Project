# management/commands/import_shareholders.py
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import csv
from un_app.models import Company, CompanyShareholder

class Command(BaseCommand):
    help = 'Import company shareholders from a CSV file'

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

        created_count = 0
        error_count = 0
        
        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                
                # Group rows by company to validate total percentages
                company_shareholders = {}
                for row_number, row in enumerate(reader, start=2):  # Start at 2 to account for header row
                    company_abbrev = row['company']
                    if company_abbrev not in company_shareholders:
                        company_shareholders[company_abbrev] = []
                    company_shareholders[company_abbrev].append((row_number, row))

                # Process each company's shareholders
                for company_abbrev, shareholders in company_shareholders.items():
                    try:
                        # Get the company
                        try:
                            company = Company.objects.get(abbreviation=company_abbrev)
                        except Company.DoesNotExist:
                            raise ValueError(f"Company not found: {company_abbrev}")

                        # Calculate total percentage for this company
                        total_percentage = sum(Decimal(row['percent']) for _, row in shareholders)
                        if total_percentage != 100:
                            raise ValueError(
                                f"Total percentage for {company_abbrev} is {total_percentage}%, must be 100%"
                            )

                        # Clear existing shareholders if not dry run
                        if not dry_run:
                            company.shareholders.all().delete()

                        # Process each shareholder
                        for row_number, row in shareholders:
                            try:
                                # Prepare shareholder data
                                shareholder_data = {
                                    'company': company,
                                    'shareholder_type': get_content_type(row['type']),
                                    'shareholder_abbreviation': row['shareholder'],
                                    'percentage': Decimal(row['percent']),
                                }

                                if dry_run:
                                    self.stdout.write(f"Would create shareholder: {shareholder_data}")
                                    created_count += 1
                                    continue

                                # Create the shareholder
                                shareholder = CompanyShareholder.objects.create(**shareholder_data)
                                created_count += 1
                                self.stdout.write(self.style.SUCCESS(
                                    f"Created shareholder: {shareholder}"
                                ))

                            except Exception as e:
                                error_count += 1
                                self.stdout.write(self.style.ERROR(
                                    f"Error on row {row_number}: {str(e)}"
                                ))

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(
                            f"Error processing company {company_abbrev}: {str(e)}"
                        ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
            return

        # Print summary
        self.stdout.write("\nImport Summary:")
        self.stdout.write(f"{'Would create' if dry_run else 'Created'} {created_count} shareholders")
        if error_count:
            self.stdout.write(self.style.ERROR(f"Encountered {error_count} errors"))