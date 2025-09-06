from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.db.models import F, Sum, Value, DecimalField
from decimal import Decimal

class Company(models.Model):
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
        # Iterate over each LiquidAssetContainer related to this company
        for container in LiquidAssetContainer.objects.filter(company=self):
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
            
            # Add to the total for the company
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
        
        # Sum of partial ownerships
        company_content_type = ContentType.objects.get_for_model(Company)
        partials_total = PartialBuildingOwnership.objects.filter(
            partial_owner_type=company_content_type,
            partial_owner_abbreviation=self.abbreviation
        ).aggregate(
            total_value=Coalesce(
                Sum('partial_price', output_field=DecimalField(max_digits=20, decimal_places=6)),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total_value'] or Decimal('0')

        return partials_total

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"
    
# --------------------------------------------------------------------
class CompanyShareholder(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='shareholders')
    shareholder_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('nation', 'company')}, help_text="The type of entity that owns shares (Nation or Company)")
    shareholder_abbreviation = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage ownership of the company")
    board_member = models.ForeignKey('Player', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        unique_together = ('company', 'shareholder_type', 'shareholder_abbreviation')
        ordering = ['-percentage']  # Order by percentage descending

    def clean(self):
        if self.percentage <= 0:
            raise ValidationError("Percentage must be greater than 0")
            
        # Validate that shareholder_abbreviation matches an existing Nation or Company
        shareholder_model = self.shareholder_type.model_class()
        if not shareholder_model.objects.filter(abbreviation=self.shareholder_abbreviation).exists():
            raise ValidationError(f"{self.shareholder_abbreviation} is not a valid {shareholder_model.__name__} abbreviation.")
            
        # Prevent a company from owning shares in itself
        if (self.shareholder_type.model == Company and 
            self.shareholder_abbreviation == self.company.abbreviation):
            raise ValidationError("A company cannot own shares in itself.")
            
        # Get total percentage excluding this instance
        existing_total = CompanyShareholder.objects.filter(company=self.company)
        if self.id:
            existing_total = existing_total.exclude(id=self.id)
        existing_total = existing_total.aggregate(
            total=Coalesce(
                Sum('percentage', output_field=models.DecimalField(max_digits=5, decimal_places=2)),
                Value(0, output_field=models.DecimalField(max_digits=5, decimal_places=2))
            )
        )['total']

        # Check if total would exceed 100%
        if existing_total + self.percentage > Decimal('100'):
            raise ValidationError(
                f"Total shareholder percentage would exceed 100%. "
                f"Current total: {existing_total}%, Attempting to add: {self.percentage}%")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def shareholder(self):
        """Get the actual shareholder instance (Nation or Company)."""
        model_class = self.shareholder_type.model_class()
        try:
            return model_class.objects.get(abbreviation=self.shareholder_abbreviation)
        except model_class.DoesNotExist:
            return None

    @property
    def shareholder_name(self):
        """Get the name of the shareholder."""
        shareholder = self.shareholder
        return shareholder.name if shareholder else self.shareholder_abbreviation

    def __str__(self):
        return f"{self.shareholder_abbreviation} owns {self.percentage}% of {self.company.abbreviation}"