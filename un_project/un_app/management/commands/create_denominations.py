from django.core.management.base import BaseCommand
from un_app.models import Denomination

class Command(BaseCommand):
    help = 'Create denomination items'

    def handle(self, *args, **kwargs):
        Denomination.objects.create(name='Netherite Ingot', diamond_equivalent=6.25)
        Denomination.objects.create(name='Diamond', diamond_equivalent=1)
        Denomination.objects.create(name='Gold Ingot', diamond_equivalent=1/24)
        Denomination.objects.create(name='Emerald', diamond_equivalent=1/192)
        Denomination.objects.create(name='Iron Ingot', diamond_equivalent=1/384)
        Denomination.objects.create(name='Copper Ingot', diamond_equivalent=1/384)
        Denomination.objects.create(name='Redstone Dust', diamond_equivalent=1/3456)
        Denomination.objects.create(name='Lapis Lazuli', diamond_equivalent=1/3456)
        Denomination.objects.create(name='Coal', diamond_equivalent=1/3456)

        self.stdout.write(self.style.SUCCESS('Successfully created denomination items'))