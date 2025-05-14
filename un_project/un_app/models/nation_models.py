from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Coalesce
from django.db.models import F, Sum, Value, DecimalField
from decimal import Decimal
#from .liquid_asset_models import LiquidAssetContainer
#from .building_models import PartialBuildingOwnership

class Nation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)
    # Precalculated fields
    total_liquid_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    total_item_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    total_building_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))

    # Calculate total liquid asset value
    def calculate_total_liquid_asset_value(self):
        from .liquid_asset_models import LiquidAssetContainer
        
        total_value = Decimal('0')
        # Iterate over each LiquidAssetContainer related to this nation
        for container in LiquidAssetContainer.objects.filter(nation=self):
            # Calculate the total diamond value for each container
            container_total = container.liquidcount_set.aggregate(
                total_value=Coalesce(
                    Sum(
                        F('count') * F('denomination__diamond_equivalent'),
                        output_field=DecimalField(max_digits=20, decimal_places=6)
                    ),
                    Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
                )
            )['total_value'] or Decimal('0')
            
            # Add to the total for the nation
            total_value += container_total
        return total_value

    # Calculate total item asset value
    def calculate_total_item_asset_value(self):
        total = self.itemcount_set.aggregate(
            total_value=Coalesce(
                Sum('total_value', output_field=DecimalField(max_digits=20, decimal_places=6)),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total_value'] or Decimal('0')
        return total

    # Calculate total building asset value
    def calculate_total_building_asset_value(self):
        from .building_models import PartialBuildingOwnership
        
        # Sum of buildings owned by the nation
        buildings_total = self.owned_buildings.aggregate(
            total_value=Coalesce(
                Sum('price_minus_partial', output_field=DecimalField(max_digits=20, decimal_places=6)),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total_value'] or Decimal('0')

        # Sum of partial ownerships
        nation_content_type = ContentType.objects.get_for_model(Nation)
        partials_total = PartialBuildingOwnership.objects.filter(
            partial_owner_type=nation_content_type,
            partial_owner_abbreviation=self.abbreviation
        ).aggregate(
            total_value=Coalesce(
                Sum('partial_price', output_field=DecimalField(max_digits=20, decimal_places=6)),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total_value'] or Decimal('0')

        return buildings_total + partials_total

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"