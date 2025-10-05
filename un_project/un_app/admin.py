from django.contrib import admin
from . import models

admin.site.register(models.Nation)
admin.site.register(models.Company)
#admin.site.register(models.Player)
#admin.site.register(models.Territory)
#admin.site.register(models.Building)
admin.site.register(models.PartialBuildingOwnership)
admin.site.register(models.BuildingEvaluation)
admin.site.register(models.BuildingEvaluationComponent)
admin.site.register(models.Denomination)
#admin.site.register(models.Item)
admin.site.register(models.ItemCount)
admin.site.register(models.ItemFixedPriceComponent)
admin.site.register(models.ItemEvaluation)
admin.site.register(models.ItemEvaluationComponent)
admin.site.register(models.UserProfile)
admin.site.register(models.LiquidCount)
admin.site.register(models.LiquidAssetContainer)
admin.site.register(models.Liability)
admin.site.register(models.LiabilityPayment)
admin.site.register(models.CompanyShareholder)


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_type', 'ordering', 'market_value')  
    search_fields = ('name', 'description', 'note', 'image_name')      
    list_filter = ('price_type',) 
    ordering = ('ordering',)
    
#-------------------------------------------------------------------------------
@admin.register(models.Building)
class BuildingAdmin(admin.ModelAdmin):
    # Columns shown in the list view
    list_display = (
        'name',
        'owner',
        'territory',
        'height',
        'year_started',
        'coordinates',
        'completed',
    )

    search_fields = (
        'name',
        'architectural_style',
        'owner__name', 
        'territory__name',
        'main_builders__username',
    )
    
    list_filter = (
        'owner',
        'completed',
        'historic_site',
        'architectural_genius',
        'mopq_award',
    )

    ordering = ('name',)
    # This makes the many-to-many field more manageable in admin
    filter_horizontal = ('main_builders',)
    
#-------------------------------------------------------------------------------
@admin.register(models.Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)  # 🔍 enables the search bar
    ordering = ('name',)
    
#-------------------------------------------------------------------------------
@admin.register(models.Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'nation',
        'un_rep',
        'num_buildings_built_display',  # custom column
    )
    search_fields = (
        'username',
        'nation__name',  # allows searching by nation name
        'nation__abbreviation'
        'description',
    )
    list_filter = ('un_rep', 'nation',)
    ordering = ('username',)

    @admin.display(description="Buildings Built")
    def num_buildings_built_display(self, obj):
        return obj.num_buildings_built()
    
#-------------------------------------------------------------------------------