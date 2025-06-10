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
    
    
#--------------------------------------------------------------------------------------------


class Treaty(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    nations_involved = models.ManyToManyField('un_app.Nation', related_name='treaty')
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the treaty was considered void")
    
    def clean(self):
        # Ensure that invalidation_date is only set when void or repealed is True
        if (self.void) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the treaty is void or repealed.")
        
        # Ensure that invalidation_date is None if neither void nor repealed is True
        if not (self.void) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the treaty is void or repealed.")

    def __str__(self):
        return f"{self.title} ({self.date})"
    
    
class TreatyImage(models.Model):
    treaty = models.ForeignKey(Treaty, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='treaty_images/')
    order = models.PositiveIntegerField(default=0, help_text="Order in which images should be displayed")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.treaty.title} ({self.order})"