from django.db import models
from django.core.exceptions import ValidationError

class Declaration_Of_War(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    nations_involved = models.ManyToManyField('un_app.Nation', related_name='declaration_of_war')
    body = models.TextField()
    resolved = models.BooleanField(default=False, blank=True)
    peace_date = models.DateField(null=True, default=None, blank=True, help_text="Date the war was resolved")
    resolving_treaty = models.ForeignKey('Treaty', on_delete=models.CASCADE, related_name='resolving_treaty', null=True, default=None, blank=True)
    
    def clean(self):
        # Ensure that invalidation_date is only set when resolved is True
        if (self.resolved) and not self.peace_date:
            raise ValidationError("Invalidation date must be set if the declaration_of_war is resolved.")
        
        # Ensure that invalidation_date is None if neither resolved is True
        if not (self.resolved) and self.peace_date:
            raise ValidationError("Invalidation date cannot be set unless the declaration_of_war is resolved.")

    def __str__(self):
        return f"{self.title} ({self.date})"