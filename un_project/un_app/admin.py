from django.contrib import admin
from .models import Nation, Player, Territory, Building, Company, PartialBuildingOwnership

admin.site.register(Nation)
admin.site.register(Company)
admin.site.register(Player)
admin.site.register(Territory)
admin.site.register(Building)
admin.site.register(PartialBuildingOwnership)