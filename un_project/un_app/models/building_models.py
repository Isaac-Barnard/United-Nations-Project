from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, Value
from decimal import Decimal
#from .territory_models import Territory
#from .nation_models import Nation
#from .player_models import Player
#from .denomination_models import Denomination

class BuildingQuerySet(models.QuerySet):
    def existing(self):
        return self.filter(destroyed=False)

    def destroyed(self):
        return self.filter(destroyed=True)
    
class ExistingBuildingManager(models.Manager):
    def get_queryset(self):
        return BuildingQuerySet(self.model, using=self._db).filter(destroyed=False)

class Building(models.Model):
    MOPQ_CHOICES = [
        ('Eligible', 'Eligible'),
        ('Nominated', 'Nominated'),
        ('Won', 'Won')
    ]
    
    SIZE_CHOICES = [
        ('Tiny', 'Tiny (-5×5)'),
        ('Very Small', 'Very Small (6×6 to 8×8)'),
        ('Small', 'Small (9×9 to 12×12)'),
        ('Modest', 'Modest (12×12 to 15×15)'),
        ('Medium-Small', 'Medium-Small (16×16 to 20×20)'),
        ('Medium', 'Medium (20×20 to 25×25)'),
        ('Medium-Large', 'Medium-Large (25×25 to 30×30)'),
        ('Large', 'Large (31×31 to 40×40)'),
        ('Very Large', 'Very Large (40×40 to 50×50)'),
        ('Huge', 'Huge (51×51 to 75×75)'),
        ('Enormous', 'Enormous (75×75 to 100×100)'),
        ('Gigantic', 'Gigantic (100×100 to 150×150)'),
        ('Massive', 'Massive (150×150+)'),
    ]
    
    MATERIAL_CHOICES = [
        ('Basic', 'Basic (Dirt, Cobblestone, Netherrack, Oak Planks...)'),
        ('Standard', 'Standard (Stone Bricks, Smooth Sandstone, Terracotta...)'),
        ('Premium', 'Premium (Smooth Stone, glazed terricotta, exotic woods and stones...)'),
        ('Elite', 'Elite (Quartz, Obsidian, Purpur, Prismarine...)'),
    ]
    
    name = models.CharField(max_length=100, unique=True, help_text="Building name")
    territory = models.ForeignKey('Territory', on_delete=models.CASCADE, related_name='buildings', null=True, help_text="The name of the territory district that this building resides. This does not necessarily indicate owner")
    owner = models.ForeignKey('Nation', on_delete=models.CASCADE, related_name='owned_buildings', help_text="The nation that owns the building as its sovereign territory")
    main_builders = models.ManyToManyField('Player', related_name='main_builds', help_text="The builder/builders who constructed the majority of the building")
    y_level_high_pt = models.FloatField(null=True, help_text="The highest point of the building")
    y_level_ground = models.FloatField(null=True, help_text="The ground level of the building. Measured to the ground level, not lowest point of the building ie. basements or mines")
    year_started = models.IntegerField(null=True, help_text="The year where construction began on the building")
    completed = models.BooleanField(default=True, help_text="Whether or not the building is completed. False means the building is incomplete")
    x_coordinate = models.CharField(max_length=50, help_text="The x-coordinate of roughly center of the build")
    z_coordinate = models.CharField(max_length=50, help_text="The z-coordinate of roughly center of the build")
    historic_site = models.BooleanField(default=False, help_text="Damage to structures in the Register of Historic and Cultural Structures (RHCS) is considered war crime") 
    architectural_genius = models.BooleanField(default=False, help_text="Damage to structures in the Register of Architectural and Engineering Wonders of the World (RAEWW) will result in court suits or settlements for damages will be doubled") 
    mopq_award = models.CharField(max_length=50, null=True, blank=True, choices=MOPQ_CHOICES, help_text="Medal of Papa Quinn (MoPQ) award for architecture or another MoPQ award related to a building.")
    architectural_style = models.CharField(max_length=100, null=True, blank=True, help_text="The architectural style of the building if it falls into one")
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, null=True, blank=True, help_text="The size category of the building")
    materials = models.CharField(max_length=20, choices=MATERIAL_CHOICES, null=True, blank=True, help_text="The primary building materials used in construction")
    furnished = models.BooleanField(null=True, blank=True, help_text="Whether the building is furnished inside")
    destroyed = models.BooleanField(default=False, help_text="Whether the building has been destroyed")
    year_destroyed = models.IntegerField(null=True, blank=True, help_text="The year the building was destroyed")
    
    # Precalculated fields
    ownership_minus_partial = models.IntegerField(default=0)
    price_minus_partial = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    
    # Filtering out destroyed buildings
    objects = ExistingBuildingManager()  # Default manager (only existing)
    all_objects = BuildingQuerySet.as_manager()  # Includes destroyed

    def save(self, *args, **kwargs):
        current_year = timezone.now().year
        if self.year_started == current_year:
            self.mopq_award = "Eligible"
        elif self.mopq_award not in ["Nominated", "Won"]:
            self.mopq_award = ""
        super().save(*args, **kwargs)
        
    def clean(self):
        if not self.destroyed and self.year_destroyed:
            raise ValidationError("Non-destroyed buildings cannot have a year_destroyed.")

    def __str__(self):
        return self.name
    
    @property
    def height(self):
        if self.y_level_high_pt is None or self.y_level_ground is None:
            return 0
        return self.y_level_high_pt - self.y_level_ground
    
    @property
    def coordinates(self):
        return f"{self.x_coordinate}/~/{self.z_coordinate}"
    
    @property
    def price(self):
        evaluations = self.building_evaluations.all()
        evaluation_count = evaluations.count()

        # If there are fewer than two evaluations, return 0 as specified
        if evaluation_count < 2:
            return Decimal('0')
    
        # Calculate the total value by summing up each evaluation's total_diamond_value
        total_value = sum(evaluation.total_diamond_value for evaluation in evaluations)

        # Calculate the average price
        avg_price = total_value / Decimal(evaluation_count)
        #return avg_price / evaluation_count
        return avg_price

    @property
    def adjusted_ownership(self):
        """
        Calculate the adjusted ownership for the building.
        Ownership is 100% minus the sum of partial owners' percentages who are not the main owner.
        """
        total_ownership = self.partialbuildingownership_set.filter(
            ~Q(partial_owner_abbreviation=self.owner.abbreviation)
        ).aggregate(
            total_ownership=Coalesce(Sum('percentage'), Value(0))
        )['total_ownership'] or 0

        return 100 - total_ownership
    
    @property
    def adjusted_ownership_price(self):
        #Calculate the adjusted ownership price by multiplying the building price by adjusted ownership.
        if self.price and self.adjusted_ownership is not None:
            return Decimal(self.price) * Decimal(self.adjusted_ownership) / Decimal(100)
        return 0  # Return None if price or adjusted ownership is missing

# --------------------------------------------------------------------
class PartialBuildingOwnership(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    partial_owner_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('nation', 'company')}  # Only allow Nation and Company
    )
    partial_owner_abbreviation = models.CharField(max_length=100)  # Must match Nation or Company abbreviation
    #partial_owner = GenericForeignKey('partial_owner_type', 'partial_owner_abbreviation')
    percentage = models.IntegerField()  # Whole percentage, no decimal places
    # Precalculated fields
    partial_price = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))

    class Meta:
        unique_together = ('building', 'partial_owner_type', 'partial_owner_abbreviation')

    def clean(self):
        """Validate that partial_owner_abbreviation matches an existing Nation or Company."""
        model_class = self.partial_owner_type.model_class()
        if not model_class.objects.filter(abbreviation=self.partial_owner_abbreviation).exists():
            raise ValidationError(f"{self.partial_owner_abbreviation} is not a valid {model_class.__name__} abbreviation.")
        
    @property
    def partial_owner(self):
        """Fetch the partial owner instance based on abbreviation."""
        model_class = self.partial_owner_type.model_class()
        try:
            return model_class.objects.get(abbreviation=self.partial_owner_abbreviation)
        except model_class.DoesNotExist:
            return None

    def partial_ownership_price(self):
        """Calculate the price based on the partial ownership percentage."""
        if self.building.price:
            return Decimal(self.building.price) * Decimal(self.percentage) / Decimal(100)
        return 0  # Return 0 if no price is available for the building

    def __str__(self):
        return f"{self.partial_owner_abbreviation} owns {self.percentage}% of {self.building.name}"
    
# --------------------------------------------------------------------
class BuildingEvaluation(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='building_evaluations')
    evaluator = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='building_evaluations', limit_choices_to={'un_rep': True})
    evaluation_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('building', 'evaluator')  # A player can only evaluate a building once

    def __str__(self):
        return f"{self.evaluator.username} evaluated {self.building.name}"

    @property
    def total_diamond_value(self):
        total = Decimal('0')
        for component in self.evaluation_components.all():
            total += Decimal(component.quantity) * Decimal(component.denomination.diamond_equivalent)
        return total
    
# --------------------------------------------------------------------
class BuildingEvaluationComponent(models.Model):
    evaluation = models.ForeignKey(BuildingEvaluation, on_delete=models.CASCADE, related_name='evaluation_components')
    denomination = models.ForeignKey('Denomination', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ('evaluation', 'denomination')


    def __str__(self):
        formatted_quantity = f"{self.quantity:.3f}"  # Format quantity to 3 decimal places
        return f'{formatted_quantity} x {self.denomination.name} x {self.evaluation}'