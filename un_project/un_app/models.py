from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Avg, F, Sum, Value
from decimal import Decimal

# --------------------------------------------------------------------
class Nation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.abbreviation
    
# --------------------------------------------------------------------
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.abbreviation
    
# --------------------------------------------------------------------
class Player(models.Model):
    username = models.CharField(max_length=100, unique=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='players')
    un_rep = models.BooleanField(default=False)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username
    
    def num_buildings_built(self):
        return self.main_builds.count()
    
# --------------------------------------------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='user_profiles')

    def __str__(self):
        return f'{self.user.username} linked to {self.player.username}'

# --------------------------------------------------------------------
class Territory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
# --------------------------------------------------------------------
class Denomination(models.Model):
    name = models.CharField(max_length=100, unique=True)
    diamond_equivalent = models.DecimalField(max_digits=20, decimal_places=15)
    priority = models.IntegerField(null=True)

    def __str__(self):
        return self.name
    
# --------------------------------------------------------------------
#                           Buildings
# --------------------------------------------------------------------
class Building(models.Model):
    name = models.CharField(max_length=100, unique=True,
                            help_text="Building name")
    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, related_name='buildings', null=True,
                                  help_text="The name of the territory district that this building resides. This does not necessarily indicate owner")
    owner = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='owned_buildings',
                              help_text="The nation that owns the building as its sovereign territory")
    main_builders = models.ManyToManyField(Player, related_name='main_builds',
                                           help_text="The builder/builders who constructed the majority of the building")
    y_level_high_pt = models.FloatField(null=True,
                                        help_text="The highest point of the building")
    y_level_ground = models.FloatField(null=True,
                                       help_text="The ground level of the building. Measured to the ground level, not lowest point of the building ie. basements or mines")
    year_completed = models.IntegerField(null=True,
                                         help_text="The year where construction began on the building")
    completed = models.BooleanField(default=True,
                                    help_text="Whether or not the building is completed. False means the building is incomplete")
    x_coordinate = models.CharField(max_length=50,
                                    help_text="The x-coordinate of roughly center of the build")
    z_coordinate = models.CharField(max_length=50,
                                    help_text="The z-coordinate of roughly center of the build")
    historic_site = models.BooleanField(default=False,
                                        help_text="Damage to structures in the Register of Historic and Cultural Structures (RHCS) is considered war crime") 
    architectural_genius = models.BooleanField(default=False,
                                               help_text="Damage to structures in the Register of Architectural and Engineering Wonders of the World (RAEWW) will result in court suits or settlements for damages will be doubled") 
    mopq_award = models.CharField(max_length=50, null=True, blank=True,
                                  choices=[
                                      ('Eligible', 'Eligible'),
                                      ('Nominated', 'Nominated'),
                                      ('Won', 'Won')
                                  ],
                                  help_text="Medal of Papa Quinn (MoPQ) award for architecture or another MoPQ award related to a building.")
    architectural_style = models.CharField(max_length=100, null=True, blank=True,
                                           help_text="The architectural style of the building if it falls into one")

    def save(self, *args, **kwargs):
        current_year = timezone.now().year
        if self.year_completed == current_year:
            self.mopq_award = "Eligible"
        elif self.mopq_award not in ["Nominated", "Won"]:
            self.mopq_award = ""
        super().save(*args, **kwargs)

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
        if evaluation_count < 2:
            return Decimal('0')

        total_value = Decimal('0')
        for evaluation in evaluations:
            total_value += evaluation.total_diamond_value
        avg_price = total_value / Decimal(evaluation_count)
        return avg_price

    @property
    def adjusted_ownership(self):
        """
        Calculate the adjusted ownership for the building.
        Ownership is 100% minus the sum of partial owners' percentages who are not the main owner.
        """
        total_ownership = self.partialbuildingownership_set.aggregate(
            total_ownership=Coalesce(
                Sum('percentage', filter=~F('partial_owner_abbreviation') == self.owner.abbreviation),
                Value(0)
            )
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
    partial_owner = GenericForeignKey('partial_owner_type', 'partial_owner_abbreviation')
    percentage = models.IntegerField()  # Whole percentage, no decimal places

    class Meta:
        unique_together = ('building', 'partial_owner_type', 'partial_owner_abbreviation')

    def clean(self):
        """Validate that partial_owner_abbreviation matches either Nation or Company."""
        if self.partial_owner_type.model == 'nation':
            if not Nation.objects.filter(abbreviation=self.partial_owner_abbreviation).exists():
                raise ValidationError(f"{self.partial_owner_abbreviation} is not a valid Nation abbreviation.")
        elif self.partial_owner_type.model == 'company':
            if not Company.objects.filter(abbreviation=self.partial_owner_abbreviation).exists():
                raise ValidationError(f"{self.partial_owner_abbreviation} is not a valid Company abbreviation.")

    @property
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
    evaluator = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='building_evaluations', limit_choices_to={'un_rep': True})
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
    denomination = models.ForeignKey(Denomination, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)

    def __str__(self):
        formatted_quantity = f"{self.quantity:.3f}"  # Format quantity to 3 decimal places
        return f'{formatted_quantity} x {self.denomination.name} x {self.evaluation}'
    
# --------------------------------------------------------------------
#                           Items
# --------------------------------------------------------------------
class Item(models.Model):
    FIXED_PRICE = 'fixed'
    MARKET_RATE = 'market'

    PRICE_TYPE_CHOICES = [
        (FIXED_PRICE, 'Fixed Price'),
        (MARKET_RATE, 'Market Rate'),
    ]

    name = models.CharField(max_length=100, unique=True)
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)  # Optional description field

    def __str__(self):
        return self.name
    
    @property
    def total_diamond_value(self):
        total = 0
        for component in self.price_components.all():
            total += component.quantity * component.denomination.diamond_equivalent
        return total
    
    @property
    def price_breakdown(self):
        return self.price_components.all()
    
    @property
    def market_price(self):
        if self.price_type == self.FIXED_PRICE:
            # Calculate the fixed price using ItemFixedPriceComponent
            total_fixed_price = sum(
                component.quantity * component.denomination.diamond_equivalent
                for component in self.price_components.all()
            )
            return total_fixed_price

        elif self.price_type == self.MARKET_RATE:
            # Calculate the market price using ItemEvaluation
            evaluations = self.item_evaluations.all()
            if not evaluations.exists():
                return Decimal('0')

            total_value = sum(evaluation.total_diamond_value for evaluation in evaluations)
            market_rate = total_value / evaluations.count()
        
            # Round to 3 decimal places for market rate items
            return market_rate.quantize(Decimal('0.001'))

        return Decimal('0')  # Default fallback if no price_type is specified

# --------------------------------------------------------------------
class ItemEvaluation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_evaluations', limit_choices_to={'price_type': 'market'})
    evaluator = models.ForeignKey(Player, on_delete=models.CASCADE, limit_choices_to={'un_rep': True})
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('item', 'evaluator')  # A player can only evaluate an item once


    def __str__(self):
        return f'{self.item.name} evaluation by {self.evaluator.username}'
    
    @property
    def total_diamond_value(self):
        total = Decimal('0')
        for component in self.evaluation_components.all():
            total += Decimal(component.quantity) * Decimal(component.denomination.diamond_equivalent)
        return total
    

class ItemEvaluationComponent(models.Model):
    evaluation = models.ForeignKey(ItemEvaluation, on_delete=models.CASCADE, related_name='evaluation_components')
    denomination = models.ForeignKey(Denomination, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)

    def __str__(self):
        return f'{self.quantity} x {self.denomination.name} x {self.evaluation}'

    
# --------------------------------------------------------------------
class ItemCount(models.Model):
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.DecimalField(max_digits=20, decimal_places=3)  # Allows for 2 decimal places

    class Meta:
        # Ensure the combination of nation and item is unique
        unique_together = ('nation', 'item')

    def __str__(self):
        return f'{self.item.name} - {self.nation.name} x {self.count}'
    
# --------------------------------------------------------------------
class ItemFixedPriceComponent(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='price_components')
    denomination = models.ForeignKey(Denomination, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        # Ensure that an item can have only one fixed price component
        unique_together = ('item',)

    def __str__(self):
        return f'{self.quantity} x {self.denomination.name} for {self.item.name}'

    def clean(self):
        # Ensure the item is a fixed price item
        if self.item.price_type != Item.FIXED_PRICE:
            raise ValidationError(f"Item '{self.item.name}' must be a fixed-price item to have a fixed price component.")
    
    def save(self, *args, **kwargs):
        # Call the clean method to perform the validation before saving
        self.clean()
        super().save(*args, **kwargs)
