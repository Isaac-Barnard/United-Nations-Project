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
    
    
#--------------------------------------------------------------------------------------------

class Executive_Order(models.Model):
    number = models.PositiveIntegerField()
    charter = models.PositiveIntegerField()
    date = models.DateField()
    ordered_by = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='ordered_executive_order')
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    repealed = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the resolution was considered void or repealed")
    
    class Meta:
        unique_together = ('number', 'charter')
    
    def clean(self):
        # Ensure that invalidation_date is only set when void or repealed is True
        if (self.void or self.repealed) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the resolution is void or repealed.")
        
        # Ensure that invalidation_date is None if neither void nor repealed is True
        if not (self.void or self.repealed) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the resolution is void or repealed.")

    def __str__(self):
        return f"Executive Order No. {self.number} ({self.date}) Charter {self.charter}"
    
    
#--------------------------------------------------------------------------------------------


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
    
    
class CharterAmendment(models.Model):
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
    
    
#--------------------------------------------------------------------------------------------


class Alliance(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    nations_involved = models.ManyToManyField('un_app.Nation', related_name='alliance')
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
    
    
#--------------------------------------------------------------------------------------------


class Declaration_Of_War(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    nations_involved = models.ManyToManyField('un_app.Nation', related_name='declaration_of_war')
    body = models.TextField()
    resolved = models.BooleanField(default=False, blank=True)
    peace_date = models.DateField(null=True, default=None, blank=True, help_text="Date the war was resolved")
    
    def clean(self):
        # Ensure that invalidation_date is only set when resolved is True
        if (self.resolved) and not self.peace_date:
            raise ValidationError("Invalidation date must be set if the declaration_of_war is resolved.")
        
        # Ensure that invalidation_date is None if neither resolved is True
        if not (self.resolved) and self.peace_date:
            raise ValidationError("Invalidation date cannot be set unless the declaration_of_war is resolved.")

    def __str__(self):
        return f"{self.title} ({self.date})"