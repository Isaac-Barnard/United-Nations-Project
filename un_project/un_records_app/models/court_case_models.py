from django.db import models
from django.core.exceptions import ValidationError
from un_app.models import Nation, Player, Company


class CourtCase(models.Model):
    case_number = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)
    date = models.DateField()
    votes_for_plaintiff = models.PositiveIntegerField(blank=True, null=True)
    votes_for_defendant = models.PositiveIntegerField(blank=True, null=True)
    ruling_body = models.TextField()
    
    plaintiff_nation = models.ManyToManyField(Nation, blank=True, related_name='plaintiff_nation')
    defendant_nation = models.ManyToManyField(Nation, blank=True, related_name='defendant_nation')
    plaintiff_individual = models.ManyToManyField(Player, blank=True, related_name='plaintiff_individual')
    defendant_individual = models.ManyToManyField(Player, blank=True, related_name='defendant_individual')
    plaintiff_company = models.ManyToManyField(Company, blank=True, related_name='plaintiff_company')
    defendant_company = models.ManyToManyField(Company, blank=True, related_name='defendant_company')

    def __str__(self):
        return f"Case {self.case_number}: {self.title} ({self.date})"
    
    
    
ARGUMENT_TYPE = [
        ('Plaintiff Argument', 'Plaintiff Argument'),
        ('Defendant Argument', 'Defendant Argument'),
        ('Concurring Opinion', 'Concurring Opinion'),
        ('Dissenting Opinion', 'Dissenting Opinion'),
        ('Witness Direct Examination', 'Witness Direct Examination'),
        ('Witness Cross Examination', 'Witness Cross Examination'),
        ('War Crime Tribunal', 'War Crime Tribunal'),
    ]
    
class CourtCaseArgument(models.Model):
    number = models.CharField(max_length=10)
    court_case = models.ForeignKey(CourtCase, on_delete=models.CASCADE, related_name='case_argued')
    argument_type = models.CharField(max_length=50, choices=ARGUMENT_TYPE)
    speaker = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='resolution_amendment', blank=True, null=True)
    body = models.TextField()
    
    class Meta:
        unique_together = ('number', 'court_case')
    
    def __str__(self):
        return f"Case {self.court_case.case_number}: {self.argument_type} {self.number}"
    
    
    
class CourtCaseArgumentImage(models.Model):
    court_case_argument = models.ForeignKey(CourtCaseArgument, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='court_case_images/')
    evidence_letter = models.CharField(max_length=1)
    order = models.PositiveIntegerField(default=0, help_text="Order in which images should be displayed")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Case {self.court_case_argument.court_case.case_number}: {self.court_case_argument.argument_type} {self.court_case_argument.number} {self.evidence_letter} ({self.order})"