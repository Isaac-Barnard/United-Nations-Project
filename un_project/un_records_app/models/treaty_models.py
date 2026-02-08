from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify

class Treaty(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255,  unique=True, editable=False)
    date = models.DateField()
    nations_involved = models.ManyToManyField('un_app.Nation', related_name='treaty')
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the treaty was considered void")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('treaty_detail', kwargs={'slug': self.slug})

    
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