from django.db import models
from django.core.exceptions import ValidationError
from un_app.models import Nation

class Resolution(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    votes_for = models.PositiveIntegerField()
    votes_against = models.PositiveIntegerField()
    proposed_by = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='proposed_resolution')
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
        return f"{self.title} ({self.date})"
    
    
class ResolutionImage(models.Model):
    resolution = models.ForeignKey(Resolution, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='resolution_images/')
    order = models.PositiveIntegerField(default=0, help_text="Order in which images should be displayed")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.resolution.title} ({self.order})"
    
    
class ResolutionAmendment(models.Model):
    number = models.CharField(max_length=10)
    resolution = models.ForeignKey(Resolution, on_delete=models.CASCADE, related_name='amended_resolution')
    date = models.DateField()
    votes_for = models.PositiveIntegerField()
    votes_against = models.PositiveIntegerField()
    proposed_by = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='resolution_amendment')
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    repealed = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the amendment was considered void or repealed")
    
    class Meta:
        unique_together = ('number', 'resolution')
    
    def clean(self):
        # Ensure that invalidation_date is only set when void or repealed is True
        if (self.void or self.repealed) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the amendment is void or repealed.")
        
        # Ensure that invalidation_date is None if neither void nor repealed is True
        if not (self.void or self.repealed) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the amendment is void or repealed.")

    def __str__(self):
        return f"{self.resolution.title} {self.number} ({self.date})"