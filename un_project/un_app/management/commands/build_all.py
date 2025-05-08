from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Import/create all data from CSV files'

    def handle(self, *args, **kwargs):
        # Retrieve the CSV file paths
        item_data_csv = os.path.join('un_app', 'data', 'item_data.csv')
        territory_data_csv = os.path.join('un_app', 'data', 'territory_data.csv')
        player_data_csv = os.path.join('un_app', 'data', 'player_data.csv')
        partial_building_data_csv = os.path.join('un_app', 'data', 'partial_building_data.csv')
        nation_data_csv = os.path.join('un_app', 'data', 'nation_data.csv')
        market_rate_item_evaluation_csv = os.path.join('un_app', 'data', 'market_rate_item_evaluations_data.csv')
        liquid_cash_container_data_csv = os.path.join('un_app', 'data', 'liquid_cash_container_data.csv')
        liquid_cash_data_csv = os.path.join('un_app', 'data', 'liquid_cash_data.csv')
        item_counts_data_csv = os.path.join('un_app', 'data', 'item_count_data.csv')
        fixed_price_item_csv = os.path.join('un_app', 'data', 'fixed_price_item_data.csv')
        company_data_csv = os.path.join('un_app', 'data', 'company_data.csv')
        building_evaluation_data_csv = os.path.join('un_app', 'data', 'building_evaluation_data.csv')
        building_data_csv = os.path.join('un_app', 'data', 'building_data.csv')
        shareholder_data_csv = os.path.join('un_app', 'data', 'shareholder_data.csv')
        liability_data_csv = os.path.join('un_app', 'data', 'liability_data.csv')
        liability_payment_data_csv = os.path.join('un_app', 'data', 'liability_payment_data.csv')
        

        
        try:
            # Import items
            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting creating denominations...\n----------------------------------------------------"))
            call_command('create_denominations')

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of nations from {nation_data_csv}...\n----------------------------------------------------"))
            call_command('import_nations', nation_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of companies from {company_data_csv}...\n----------------------------------------------------"))
            call_command('import_companies', company_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of players from {player_data_csv}...\n----------------------------------------------------"))
            call_command('import_players', player_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting creating users...\n----------------------------------------------------"))
            call_command('create_users')

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of territories from {territory_data_csv}...\n----------------------------------------------------"))
            call_command('import_territories', territory_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of buildings from {building_data_csv}...\n----------------------------------------------------"))
            call_command('import_buildings', building_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of items from {item_data_csv}...\n----------------------------------------------------"))
            call_command('import_items', item_data_csv)
            
            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of market rate item evaluations from {market_rate_item_evaluation_csv}...\n----------------------------------------------------"))
            call_command('import_market_item_evaluations', market_rate_item_evaluation_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of liquid cash from {liquid_cash_data_csv}...\n----------------------------------------------------"))
            call_command('import_liquid_containers', liquid_cash_container_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of liquid cash from {liquid_cash_data_csv}...\n----------------------------------------------------"))
            call_command('import_liquid_count', liquid_cash_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of fixed price items from {fixed_price_item_csv}...\n----------------------------------------------------"))
            call_command('import_fixed_item_prices', fixed_price_item_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of building evaluations from {building_evaluation_data_csv}...\n----------------------------------------------------"))
            call_command('import_building_evaluations', building_evaluation_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of partial building ownership from {partial_building_data_csv}...\n----------------------------------------------------"))
            call_command('import_partial_buildings', partial_building_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of item counts from {item_counts_data_csv}...\n----------------------------------------------------"))
            call_command('import_item_counts', item_counts_data_csv)

            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of shareholders from {shareholder_data_csv}...\n----------------------------------------------------"))
            call_command('import_shareholders', shareholder_data_csv)
            
            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of liability from {liability_data_csv}...\n----------------------------------------------------"))
            call_command('import_liabilities', liability_data_csv)
            
            self.stdout.write(self.style.SUCCESS(f"----------------------------------------------------\nStarting import of liability payments from {liability_payment_data_csv}...\n----------------------------------------------------"))
            call_command('import_liability_payments', liability_payment_data_csv)


            self.stdout.write(self.style.SUCCESS('All imports completed successfully!'))

        except CommandError as e:
            self.stdout.write(self.style.ERROR(f"Error during import: {e}"))
