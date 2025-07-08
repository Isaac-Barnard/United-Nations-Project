from django.db import models
from django.core.exceptions import ValidationError
from un_app.models import Nation

class NationalConstitution(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField(unique=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='nation_constitution')
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the nation's constitution was considered void or repealed")
    
    def clean(self):
        # Ensure that invalidation_date is only set when void or repealed is True
        if (self.void) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the nation's constitution is void")
        
        # Ensure that invalidation_date is None if neither void nor repealed is True
        if not (self.void) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the nation's constitution is void")

    def __str__(self):
        return f"{self.nation.abbreviation} - {self.title} ({self.date})"
    
    
class NationalConstitutionAmendment(models.Model):
    title = models.CharField(max_length=255)
    national_constitution = models.ForeignKey(NationalConstitution, on_delete=models.CASCADE, related_name='amended_national_constitution')
    date = models.DateField()
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the amendment was considered void or repealed")
    
    def clean(self):
        # Ensure that invalidation_date is only set when void or repealed is True
        if (self.void) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the amendment is void or repealed.")
        
        # Ensure that invalidation_date is None if neither void nor repealed is True
        if not (self.void) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the amendment is void or repealed.")

    def __str__(self):
        return f"{self.national_constitution} {self.title} ({self.date})"