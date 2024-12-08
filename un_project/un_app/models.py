from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Avg, F, Q, Sum, Value, DecimalField
from decimal import Decimal

# --------------------------------------------------------------------
class Nation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)
    # Precalculated fields
    total_liquid_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    total_item_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    total_building_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))

    # Calculate total liquid asset value
    def calculate_total_liquid_asset_value(self):
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
    
# --------------------------------------------------------------------
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)
    # Precalculated fields
    total_liquid_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    total_item_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    total_building_asset_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))

    # Calculate total liquid asset value
    def calculate_total_liquid_asset_value(self):
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
    shareholder_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('nation', 'company')},
        help_text="The type of entity that owns shares (Nation or Company)"
    )
    shareholder_abbreviation = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, 
        help_text="Percentage ownership of the company")
    
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
#                        Liquid Assets
# --------------------------------------------------------------------
class LiquidAssetContainer(models.Model):
    name = models.CharField(max_length=100)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    ordering = models.IntegerField(default=0)  # Field for manual ordering
    
    class Meta:
        # Ensure the combination of nation/company and item is unique
        constraints = [
            models.UniqueConstraint(fields=['nation', 'name'], name='unique_nation_asset'),
            models.UniqueConstraint(fields=['company', 'name'], name='unique_company_asset'),
            models.CheckConstraint(
                check=(
                    models.Q(nation__isnull=False, company__isnull=True) |
                    models.Q(nation__isnull=True, company__isnull=False)
                ),
                name='nation_or_company_asset_not_both'
            )
        ]

    def __str__(self):
        if self.nation:
            return f'{self.nation.abbreviation} - ({self.name})'
        elif self.company:
            return f'{self.company.abbreviation} - ({self.name})'
        return f'{self.name}'

# --------------------------------------------------------------------
class LiquidCount(models.Model):
    asset_container = models.ForeignKey(LiquidAssetContainer, on_delete=models.CASCADE, null=True, blank=True)
    denomination = models.ForeignKey(Denomination, on_delete=models.CASCADE)
    count = models.DecimalField(max_digits=20, decimal_places=3)  # Allows for 2 decimal places

    class Meta:
        # Ensure the combination of nation/company and item is unique
        constraints = [
            models.UniqueConstraint(fields=['asset_container', 'denomination'], name='unique_nation_asset_denomination'),
            models.UniqueConstraint(fields=['asset_container', 'denomination'], name='unique_company_asset_enomination'),
            models.UniqueConstraint(fields=['asset_container', 'denomination'], name='unique_asset_denomination'),
        ]

    def __str__(self):
        if self.asset_container.nation:
            return f'({self.asset_container}) - {self.denomination.name} x {self.count}'
        elif self.asset_container.company:
            return f'({self.asset_container}) - {self.denomination.name} x {self.count}'
        return f'{self.denomination.name} x {self.count}'


# --------------------------------------------------------------------
#                           Liability
# --------------------------------------------------------------------
class Liability(models.Model):
    LOAN = 'loan'
    MORTGAGE = 'mortgage'
    FINE = 'fine'
    PROMISE = 'promise'
    OTHER = 'other'
    
    LIABILITY_TYPE_CHOICES = [
        (LOAN, 'Loan'),
        (MORTGAGE, 'Mortgage'),
        (FINE, 'Fine'),
        (PROMISE, 'Promise of Payment'),
        (OTHER, 'Other'),
    ]
    
    debtor_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='debtor_liabilities',
        limit_choices_to={'model__in': ('nation', 'company')},
        help_text="The entity that owes the liability"
    )
    debtor_abbreviation = models.CharField(max_length=100)
    
    creditor_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='creditor_liabilities',
        limit_choices_to={'model__in': ('nation', 'company')},
        help_text="The entity that is owed the liability"
    )
    creditor_abbreviation = models.CharField(max_length=100)
    
    liability_type = models.CharField(max_length=10, choices=LIABILITY_TYPE_CHOICES)
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    total_diamond_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    # Calculated value
    remaining_diamond_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    
    def clean(self):
        # Validate that debtor_abbreviation matches an existing Nation or Company
        debtor_model = self.debtor_type.model_class()
        if not debtor_model.objects.filter(abbreviation=self.debtor_abbreviation).exists():
            raise ValidationError(f"{self.debtor_abbreviation} is not a valid {debtor_model.__name__} abbreviation.")
            
        # Validate that creditor_abbreviation matches an existing Nation or Company
        creditor_model = self.creditor_type.model_class()
        if not creditor_model.objects.filter(abbreviation=self.creditor_abbreviation).exists():
            raise ValidationError(f"{self.creditor_abbreviation} is not a valid {creditor_model.__name__} abbreviation.")
            
        # Prevent self-liability
        if (self.debtor_type == self.creditor_type and 
            self.debtor_abbreviation == self.creditor_abbreviation):
            raise ValidationError("An entity cannot owe a liability to itself.")
    
    def save(self, *args, **kwargs):
        if not self.id:  # If this is a new liability
            self.remaining_diamond_value = self.total_diamond_value
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.debtor_abbreviation} owes {self.creditor_abbreviation} - {self.get_liability_type_display()}"
    
    @property
    def is_paid(self):
        return self.remaining_diamond_value == 0

    @property
    def debtor(self):
        """Get the actual debtor instance (Nation or Company)."""
        model_class = self.debtor_type.model_class()
        try:
            return model_class.objects.get(abbreviation=self.debtor_abbreviation)
        except model_class.DoesNotExist:
            return None

    @property
    def debtor_name(self):
        """Get the full name of the debtor."""
        debtor = self.debtor
        return debtor.name if debtor else self.debtor_abbreviation

# --------------------------------------------------------------------

class LiabilityPayment(models.Model):
    liability = models.ForeignKey(Liability, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(null=True, blank=True)
    diamond_amount = models.DecimalField(max_digits=20, decimal_places=6)
    payment_number = models.IntegerField()

    class Meta:
        unique_together = ('liability', 'payment_number')

    def clean(self):
        # Get total of all payments excluding this one if it exists
        other_payments = LiabilityPayment.objects.filter(liability=self.liability)
        if self.id:
            other_payments = other_payments.exclude(id=self.id)
        
        total_other_payments = other_payments.aggregate(
            total=models.Sum('diamond_amount'))['total'] or Decimal('0')
            
        # Check if this payment would exceed the total liability
        if total_other_payments + self.diamond_amount > self.liability.total_diamond_value:
            raise ValidationError("Total payments cannot exceed the total liability amount.")
    
    def __str__(self):
        return f"Payment of {self.diamond_amount} diamonds for {self.liability} (Payment: {self.payment_number})"

# --------------------------------------------------------------------
#                           Receivables
# --------------------------------------------------------------------


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
    # Precalculated fields
    ownership_minus_partial = models.IntegerField(default=0)
    price_minus_partial = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))

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

    class Meta:
        unique_together = ('evaluation', 'denomination')


    def __str__(self):
        formatted_quantity = f"{self.quantity:.3f}"  # Format quantity to 3 decimal places
        return f'{formatted_quantity} x {self.denomination.name} x {self.evaluation}'
    
# --------------------------------------------------------------------
#                           Items
# --------------------------------------------------------------------
class Item(models.Model):
    FIXED_PRICE = 'fixed_price'
    MARKET_RATE = 'market_rate'
    SECTION_DIVIDER = 'section_divider'

    PRICE_TYPE_CHOICES = [
        (FIXED_PRICE, 'Fixed Price'),
        (MARKET_RATE, 'Market Rate'),
        (SECTION_DIVIDER, 'Section Divider'),
    ]

    name = models.CharField(max_length=100, unique=True)
    price_type = models.CharField(max_length=15, choices=PRICE_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)  # Optional description field
    ordering = models.IntegerField(default=0)  # Field for manual ordering (100's for first table, 200's for second, etc. (ex: 101, 203, 459))
    # Precalculated values:
    market_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))

    def __str__(self):
        return self.name
    

    def _total_diamond_value(self, processed_items=None):
        if processed_items is None:
            processed_items = set()
        if self.id in processed_items:
            return Decimal('0')
        processed_items.add(self.id)

        total = Decimal('0')
        for component in self.price_components.all():
            if component.denomination:
                total += Decimal(component.quantity) * Decimal(component.denomination.diamond_equivalent)
            elif component.referenced_item:
                referenced_item = component.referenced_item
                if referenced_item.price_type == self.FIXED_PRICE:
                    # Recursively calculate the price
                    referenced_item_price = referenced_item._total_diamond_value(processed_items)
                elif referenced_item.price_type == self.MARKET_RATE:
                    # Use the market price
                    referenced_item_price = referenced_item.market_price
                else:
                    # If the price type is SECTION_DIVIDER or undefined, treat price as zero
                    referenced_item_price = Decimal('0')
                
                # Apply the percentage, which may be negative
                percentage = Decimal(component.percentage_of_item)
                total += (percentage / Decimal('100')) * referenced_item_price
        return total
    
    @property
    def total_diamond_value(self):
        return self._total_diamond_value()
    
    @property
    def price_breakdown(self):
        return self.price_components.all()
    
    @property
    def market_price(self):
        if self.price_type == self.FIXED_PRICE:
            return self.total_diamond_value
        elif self.price_type == self.MARKET_RATE:
            evaluations = self.item_evaluations.all()
            if not evaluations.exists():
                return Decimal('0')
            _total_value = sum(evaluation.total_diamond_value for evaluation in evaluations)
            market_rate = _total_value / evaluations.count()
            return market_rate.quantize(Decimal('0.000001'))
        return Decimal('0')


# --------------------------------------------------------------------
class ItemEvaluation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_evaluations', limit_choices_to={'price_type': 'market_rate'})
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
    
# --------------------------------------------------------------------
class ItemEvaluationComponent(models.Model):
    evaluation = models.ForeignKey(ItemEvaluation, on_delete=models.CASCADE, related_name='evaluation_components')
    denomination = models.ForeignKey(Denomination, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ('evaluation', 'denomination')

    def __str__(self):
        return f'{self.quantity} x {self.denomination.name} x {self.evaluation}'

    
# --------------------------------------------------------------------
class ItemCount(models.Model):
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.DecimalField(max_digits=20, decimal_places=3)
    # Precalculated Values:
    total_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))

    class Meta:
        # Ensure the combination of nation/company and item is unique
        constraints = [
            models.UniqueConstraint(fields=['nation', 'item'], name='unique_nation_item'),
            models.UniqueConstraint(fields=['company', 'item'], name='unique_company_item'),
            models.CheckConstraint(
                check=(
                    models.Q(nation__isnull=False, company__isnull=True) |
                    models.Q(nation__isnull=True, company__isnull=False)
                ),
                name='nation_or_company_not_both'
            )
        ]

    def __str__(self):
        if self.nation:
            return f'{self.item.name} - {self.nation.name} x {self.count}'
        elif self.company:
            return f'{self.item.name} - {self.company.name} x {self.count}'
        return f'{self.item.name} x {self.count}'
    
# --------------------------------------------------------------------
class ItemFixedPriceComponent(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='price_components')
    denomination = models.ForeignKey(Denomination, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    referenced_item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True, related_name='referenced_in_components')
    percentage_of_item = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, help_text="Percentage of the referenced item's price to use (Ex: 50 = 50%)")

    class Meta:
        # Ensure that an item can have multiple price components but unique combinations of item, denomination, or referenced item
        constraints = [
            models.UniqueConstraint(fields=['item', 'denomination', 'referenced_item'], name='unique_price_component'),
        ]


    def clean(self):
        # Ensure that either denomination or referenced_item is provided, but not both
        if not self.denomination and not self.referenced_item:
            raise ValidationError("A price component must have either a denomination or a referenced item.")
        if self.denomination and self.referenced_item:
            raise ValidationError("A price component cannot have both a denomination and a referenced item.")
        
        # Ensure that if referenced_item is provided, percentage_of_item must also be provided
        if self.referenced_item and not self.percentage_of_item:
            raise ValidationError("When using a referenced item, a percentage of that item’s price must be specified.")
        
        # Ensure the item is a fixed-price item
        if self.item.price_type != Item.FIXED_PRICE:
            raise ValidationError(f"Item '{self.item.name}' must be a fixed-price item to have a fixed price component.")
        
        if self.denomination:
            if self.quantity is None:
                raise ValidationError("Quantity must be specified when using a denomination.")
        elif self.referenced_item:
            if self.percentage_of_item is None:
                raise ValidationError("Percentage of item must be specified when referencing another item.")

    def save(self, *args, **kwargs):
        # Call the clean method to validate before saving
        self.clean()
        super().save(*args, **kwargs)


    def __str__(self):
            if self.denomination:
                return f'{self.quantity} x {self.denomination.name} for {self.item.name}'
            elif self.referenced_item:
                return f'{self.percentage_of_item}% of {self.referenced_item.name} for {self.item.name}'
            return f'Component for {self.item.name}'
    
    @property
    def related_item_counts(self):
        """Get all ItemCount instances related to this component's item."""
        return ItemCount.objects.filter(item=self.item)