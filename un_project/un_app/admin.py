from django.contrib import admin
from .models import Nation, Player, Territory, Company, Building, BuildingEvaluation, BuildingEvaluationComponent, PartialBuildingOwnership, Denomination, Item, ItemFixedPriceComponent, ItemEvaluation, ItemEvaluationComponent, ItemCount, UserProfile

admin.site.register(Nation)
admin.site.register(Company)
admin.site.register(Player)
admin.site.register(Territory)
admin.site.register(Building)
admin.site.register(PartialBuildingOwnership)
admin.site.register(BuildingEvaluation)
admin.site.register(BuildingEvaluationComponent)
admin.site.register(Denomination)
admin.site.register(Item)
admin.site.register(ItemCount)
admin.site.register(ItemFixedPriceComponent)
admin.site.register(ItemEvaluation)
admin.site.register(ItemEvaluationComponent)
admin.site.register(UserProfile)