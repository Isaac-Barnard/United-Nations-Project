from django.db import models
from django.core.exceptions import ValidationError
from un_app.models import Nation

class Charter(models.Model):
    date = models.DateField(unique=True)
    votes_for = models.PositiveIntegerField()
    votes_against = models.PositiveIntegerField()
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    repealed = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the resolution was considered void or repealed")
    
    def clean(self):
        # Ensure that invalidation_date is only set when void or repealed is True
        if (self.void or self.repealed) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the resolution is void or repealed.")
        
        # Ensure that invalidation_date is None if neither void nor repealed is True
        if not (self.void or self.repealed) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the resolution is void or repealed.")

    def __str__(self):
        return f"{self.date}"
    
    
class Charter_Amendment(models.Model):
    number = models.CharField(max_length=10)
    charter = models.ForeignKey(Charter, on_delete=models.CASCADE, related_name='amended_charter')
    date = models.DateField()
    votes_for = models.DecimalField(max_digits=20, decimal_places=3)
    votes_against = models.DecimalField(max_digits=20, decimal_places=3)
    proposed_by = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='charter_amendment')
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    repealed = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the amendment was considered void or repealed")
    
    class Meta:
        unique_together = ('number', 'charter')
    
    def clean(self):
        # Ensure that invalidation_date is only set when void or repealed is True
        if (self.void or self.repealed) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the amendment is void or repealed.")
        
        # Ensure that invalidation_date is None if neither void nor repealed is True
        if not (self.void or self.repealed) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the amendment is void or repealed.")

    def __str__(self):
        return f"{self.charter} {self.number} ({self.date})"