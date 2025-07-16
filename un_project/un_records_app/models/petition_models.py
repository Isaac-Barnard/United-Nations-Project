from django.db import models
from django.core.exceptions import ValidationError
from un_app.models import Nation

PETITION_TYPE = [
        ('Petition to Build into Maritime Territory', 'Petition to Build into Maritime Territory'),
        ('Motion to Enter Buildings into the Register of Historic and Cultural Structures', 'Motion to Enter Buildings into the Register of Historic and Cultural Structures'),
        ('Motion for Admission into the United Nations', 'Motion for Admission into the United Nations'),
    ]
    
    
class Petition(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    petition_type = models.CharField(max_length=100, choices=PETITION_TYPE)
    petitioner = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='petitioner_nation')
    votes_for = models.PositiveIntegerField()
    votes_against = models.PositiveIntegerField()
    body = models.TextField()
    

    def __str__(self):
        return f"{self.title} ({self.date})"
    
    
class PetitionImage(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='petition_images/')
    order = models.PositiveIntegerField(default=0, help_text="Order in which images should be displayed")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.petition.title} ({self.order})"