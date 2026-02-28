from django.contrib import admin
from . import models
from django.utils.html import format_html

#admin.site.register(models.Nation)
admin.site.register(models.NationHistory)
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

@admin.register(models.Nation)
class NationAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_type', 'ordering', 'market_value')  
    search_fields = ('name', 'description', 'note', 'image_name')      
    list_filter = ('price_type',) 
    ordering = ('ordering',)
    
#-------------------------------------------------------------------------------
from django.contrib import admin
from django.utils.html import format_html
from . import models


@admin.register(models.Building)
class BuildingAdmin(admin.ModelAdmin):
    # Columns shown in the list view
    list_display = (
        'name_display',
        'owner',
        'territory',
        'height',
        'year_started',
        'year_destroyed',
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
        'year_destroyed',  # allows filtering destroyed vs existing
    )

    ordering = ('name',)

    filter_horizontal = ('main_builders',)

    # -----------------------------------------
    # Custom Name Display (Strikethrough if destroyed)
    # -----------------------------------------
    @admin.display(description="Name", ordering="name")
    def name_display(self, obj):
        if obj.year_destroyed:
            return format_html(
                "<span style='text-decoration: line-through; color: #999;'>{}</span>",
                obj.name
            )
        return obj.name

    # -----------------------------------------
    # Optional: Show destroyed buildings in admin
    # even if you made a default manager filtering them out
    # -----------------------------------------
    def get_queryset(self, request):
        # Use all_objects if you implemented soft-delete manager
        if hasattr(models.Building, "all_objects"):
            return models.Building.all_objects.all()
        return super().get_queryset(request)
    
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