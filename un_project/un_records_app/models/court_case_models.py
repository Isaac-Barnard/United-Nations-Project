from django.db import models
from django.core.exceptions import ValidationError
from un_app.models import Nation, Player, Company


class CourtCase(models.Model):
    case_number = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    votes_innocent = models.PositiveIntegerField()
    votes_guilty = models.PositiveIntegerField()
    ruling_body = models.TextField()
    
    defendant_nation = models.ForeignKey(Nation, on_delete=models.CASCADE, null=True, blank=True, related_name='defendant_nation')
    plaintiff_nation = models.ForeignKey(Nation, on_delete=models.CASCADE, null=True, blank=True, related_name='plaintiff_nation')
    defendant_individual = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='defendant_individual')
    plaintiff_individual = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='plaintiff_individual')
    defendant_company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='defendant_company')
    plaintiff_company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='plaintiff_company')

    def clean(self):
        super().clean()

        # Group defendants and plaintiffs
        defendants = [self.defendant_nation, self.defendant_individual, self.defendant_company]
        plaintiffs = [self.plaintiff_nation, self.plaintiff_individual, self.plaintiff_company]

        # Count non-null values
        num_defendants = sum(1 for d in defendants if d is not None)
        num_plaintiffs = sum(1 for p in plaintiffs if p is not None)

        if num_defendants != 1:
            raise ValidationError("Exactly one defendant must be specified.")
        if num_plaintiffs != 1:
            raise ValidationError("Exactly one plaintiff must be specified.")

    def __str__(self):
        return f"{self.title} ({self.date})"
    
    
# SIZE_CHOICES = [
#         ('Plaintiff Argument'),
#         ('Defendant Argument'),
#         ('Concurring Opinion'),
#         ('Dissenting Opinion'),
#         ('Witness Direct Examination'),
#         ('Witness Cross Examination'),
#     ]

    
# class Court_Case_Argument(models.Model):
#     number = models.CharField(max_length=10)
#     Court_Case = models.ForeignKey(Court_Case, on_delete=models.CASCADE, related_name='case_argued')
#     size = models.CharField(max_length=20, choices=SIZE_CHOICES, null=True, blank=True,
#                            help_text="The size category of the building")
#     proposed_by = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='resolution_amendment')
#     body = models.TextField()
    
#     class Meta:
#         unique_together = ('number', 'Court_Case')
    
#     def __str__(self):
#         return f"{self.Court_Case.title} {self.number}"
    
    
# class Court_Case_Image(models.Model):
#     Court_Case_Component = models.ForeignKey(Court_Case_Argument, on_delete=models.CASCADE, related_name='images')
#     image = models.ImageField(upload_to='court_case_images/')
#     order = models.PositiveIntegerField(default=0, help_text="Order in which images should be displayed")
    
#     class Meta:
#         ordering = ['order']
    
#     def __str__(self):
#         return f"Image for {self.Court_Case.title} ({self.order})"