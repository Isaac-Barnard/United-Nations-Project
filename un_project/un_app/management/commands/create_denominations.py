from django.core.management.base import BaseCommand
from un_app.models import Denomination

class Command(BaseCommand):
    help = 'Create denomination items'

    def handle(self, *args, **kwargs):
        from django.core.management.base import BaseCommand
from un_app.models import Denomination

class Command(BaseCommand):
    help = 'Create denomination items'

    def handle(self, *args, **kwargs):
        # List of denomination data
        denominations = [
            {'name': 'Netherite Ingot', 'diamond_equivalent': 6.25},
            {'name': 'Diamond', 'diamond_equivalent': 1},
            {'name': 'Gold Ingot', 'diamond_equivalent': 1/24},
            {'name': 'Emerald', 'diamond_equivalent': 1/192},
            {'name': 'Iron Ingot', 'diamond_equivalent': 1/384},
            {'name': 'Copper Ingot', 'diamond_equivalent': 1/384},
            {'name': 'Redstone Dust', 'diamond_equivalent': 1/3456},
            {'name': 'Lapis Lazuli', 'diamond_equivalent': 1/3456},
            {'name': 'Coal', 'diamond_equivalent': 1/3456},
        ]

        for denom in denominations:
            # Get or create each denomination
            obj, created = Denomination.objects.get_or_create(
                name=denom['name'],
                defaults={'diamond_equivalent': denom['diamond_equivalent']}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created denomination: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped existing denomination: {obj.name}"))

        self.stdout.write(self.style.SUCCESS('Denomination creation process completed!'))