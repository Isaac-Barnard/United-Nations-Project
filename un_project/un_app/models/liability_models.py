from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from decimal import Decimal

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