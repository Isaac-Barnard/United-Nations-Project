from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.db.models import Avg, F, Sum, Value
from decimal import Decimal

class Nation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.abbreviation
    

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.abbreviation
    

class Player(models.Model):
    username = models.CharField(max_length=100, unique=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='players')
    un_rep = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    def num_buildings_built(self):
        return self.main_builds.count()


class Territory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    #nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='territories')

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=100, unique=True)
    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, related_name='buildings', null=True)
    owner = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='owned_buildings')
    main_builders = models.ManyToManyField(Player, related_name='main_builds')
    y_level_high_pt = models.FloatField(null=True)
    y_level_ground = models.FloatField(null=True)
    year_completed = models.IntegerField(null=True)
    completed = models.BooleanField(default=True)
    x_coordinate = models.CharField(max_length=50)
    z_coordinate = models.CharField(max_length=50)
    historic_site = models.BooleanField(default=False) 
    architectural_genius = models.BooleanField(default=False) 
    mopq_award = models.CharField(max_length=50, null=True, blank=True)
    architectural_style = models.CharField(max_length=100, null=True, blank=True)

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
        # Check if the building has two or more evaluations
        evaluation_count = self.building_evaluations.count()
        if evaluation_count < 2:
            return 0
        
        # Calculate the average evaluation price
        avg_price = self.building_evaluations.aggregate(Avg('evaluation_price'))['evaluation_price__avg']
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
        """
        Calculate the adjusted ownership price by multiplying the building price by adjusted ownership.
        """
        if self.price and self.adjusted_ownership is not None:
            return Decimal(self.price) * Decimal(self.adjusted_ownership) / Decimal(100)
        return 0  # Return None if price or adjusted ownership is missing
    
    
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

    def __str__(self):
        return f"{self.partial_owner_abbreviation} owns {self.percentage}% of {self.building.name}"
    

class BuildingEvaluation(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='building_evaluations')
    evaluator = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='building_evaluations', limit_choices_to={'un_rep': True})
    evaluation_price = models.DecimalField(max_digits=12, decimal_places=10)
    evaluation_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('building', 'evaluator')  # A player can only evaluate a building once

    def __str__(self):
        return f"{self.evaluator.username} evaluated {self.building.name} at {self.evaluation_price}"
    

class Item(models.Model):
    FIXED_PRICE = 'fixed'
    MARKET_RATE = 'market'

    PRICE_TYPE_CHOICES = [
        (FIXED_PRICE, 'Fixed Price'),
        (MARKET_RATE, 'Market Rate'),
    ]

    name = models.CharField(max_length=100)
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES)
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def price(self):
        # For fixed price items, return the fixed price
        if self.price_type == self.FIXED_PRICE:
            return self.fixed_price
        
        # For market rate items, calculate the average price from evaluations
        evaluation_count = self.item_evaluations.count()
        if evaluation_count < 2:
            return 0

        avg_price = self.item_evaluations.aggregate(Avg('value'))['value__avg']
        return avg_price


class ItemEvaluation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_evaluations', limit_choices_to={'price_type': 'market'})
    evaluator = models.ForeignKey(Player, on_delete=models.CASCADE, limit_choices_to={'un_rep': True})
    value = models.DecimalField(max_digits=20, decimal_places=10)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.item.name} - {self.value} by {self.evaluator.username}'
    

class ItemCount(models.Model):
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.DecimalField(max_digits=10, decimal_places=2)  # Allows for 2 decimal places

    def __str__(self):
        return f'{self.item.name} - {self.nation.name}'