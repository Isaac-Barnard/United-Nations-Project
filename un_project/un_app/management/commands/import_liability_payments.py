# management/commands/import_liability_payments.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Max
from datetime import datetime
import csv
from decimal import Decimal
from un_app.models import Liability, LiabilityPayment

class Command(BaseCommand):
    help = 'Import liability payments from a CSV file'

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

        def parse_date(date_str):
            """Parse date string into timezone-aware datetime object"""
            if not date_str:
                # If no date provided, use current time
                return timezone.now()
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
                    datetime.combine(parsed_date.date(), datetime.min.time()),
                    timezone=timezone.get_default_timezone()
                )
            except Exception as e:
                raise ValueError(f"Error parsing date '{date_str}': {str(e)}")

        def find_liability(description):
            """Find liability by description"""
            # Try exact match first
            liability = Liability.objects.filter(description=description).first()
            
            if liability:
                return liability
            
            # If no exact match, try case-insensitive partial match
            liabilities = Liability.objects.filter(description__icontains=description)
            
            if liabilities.count() == 0:
                raise ValueError(f"No liability found matching description: {description}")
            elif liabilities.count() > 1:
                raise ValueError(f"Multiple liabilities found matching description: {description}")
            
            return liabilities.first()

        def get_next_payment_number(liability):
            """Get the next payment number for a liability"""
            max_number = LiabilityPayment.objects.filter(liability=liability).aggregate(
                Max('payment_number'))['payment_number__max']
            return 1 if max_number is None else max_number + 1

        created_count = 0
        error_count = 0
        
        # Dictionary to keep track of payment numbers for each liability
        liability_payment_numbers = {}
        
        try:
            # First pass: validate all rows and collect liabilities
            liabilities_to_update = set()
            rows_to_process = []
            
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                
                for row_number, row in enumerate(reader, start=2):
                    try:
                        liability = find_liability(row['liability'])
                        liabilities_to_update.add(liability)
                        rows_to_process.append((row_number, row, liability))
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(
                            f"Error on row {row_number}: {str(e)}"
                        ))

            # Initialize payment numbers for each liability
            for liability in liabilities_to_update:
                liability_payment_numbers[liability.id] = get_next_payment_number(liability)

            # Second pass: create payments
            for row_number, row, liability in rows_to_process:
                try:
                    # Get the next payment number for this liability
                    payment_number = liability_payment_numbers[liability.id]
                    
                    # Prepare payment data
                    payment_data = {
                        'liability': liability,
                        'payment_date': parse_date(row['payment_date']),
                        'diamond_amount': Decimal(row['diamond_amount']),
                        'payment_number': payment_number
                    }

                    if dry_run:
                        self.stdout.write(f"Would create payment #{payment_number}: {payment_data}")
                        created_count += 1
                        liability_payment_numbers[liability.id] += 1
                        continue

                    # Create the payment
                    try:
                        payment = LiabilityPayment.objects.create(**payment_data)
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"Created payment #{payment_number} of {payment.diamond_amount} diamonds for liability: {liability}"
                        ))
                        liability_payment_numbers[liability.id] += 1
                    except Exception as e:
                        raise ValueError(f"Failed to create payment: {str(e)}")

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
        self.stdout.write(f"{'Would create' if dry_run else 'Created'} {created_count} payments")
        if error_count:
            self.stdout.write(self.style.ERROR(f"Encountered {error_count} errors"))
            
        # Print remaining balances for affected liabilities
        if not dry_run and created_count > 0:
            self.stdout.write("\nUpdated Liability Balances:")
            for liability in liabilities_to_update:
                payments = LiabilityPayment.objects.filter(liability=liability).order_by('payment_number')
                self.stdout.write(f"\nLiability: {liability}")
                self.stdout.write(f"Total Value: {liability.total_diamond_value}")
                self.stdout.write(f"Remaining Value: {liability.remaining_diamond_value}")
                self.stdout.write("Payments:")