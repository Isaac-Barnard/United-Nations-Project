from django.db import models
from django.core.exceptions import ValidationError
from un_app.models import Nation

class Alliance(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    member_nations = models.ManyToManyField('un_app.Nation', related_name='alliance')
    partial_member_nations = models.ManyToManyField('un_app.Nation', related_name='partial_alliance', default=None, blank=True)
    body = models.TextField()
    defunct = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the alliance was considered defunct")
    
    def clean(self):
        # Ensure that invalidation_date is only set when defunct is True
        if (self.defunct) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the alliance is defunct.")
        
        # Ensure that invalidation_date is None if neither defunct is True
        if not (self.defunct) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the alliance is defunct.")

    def __str__(self):
        return f"{self.title} ({self.date})"
    
    
class AllianceImage(models.Model):
    alliance = models.ForeignKey(Alliance, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='alliance_images/')
    order = models.PositiveIntegerField(default=0, help_text="Order in which images should be displayed")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.alliance.title} ({self.order})"