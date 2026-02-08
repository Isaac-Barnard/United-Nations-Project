from django.db import models
from django.core.exceptions import ValidationError
from un_app.models import Nation, Player, Company
from django.urls import reverse
from django.utils.text import slugify

class CourtCase(models.Model):
    case_number = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"case-{self.case_number}-{self.title}")
            self.slug = base
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('court_case_detail', kwargs={'slug': self.slug})
    
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
        return f"Case {self.court_case.case_number}: {self.argument_type} {self.number} ({self.speaker})"
    
    
    
class CourtCaseArgumentImage(models.Model):
    court_case_argument = models.ForeignKey(CourtCaseArgument, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='court_case_images/')
    evidence_letter = models.CharField(max_length=1)
    order = models.PositiveIntegerField(default=0, help_text="Order in which images should be displayed")
    description = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Case {self.court_case_argument.court_case.case_number}: {self.court_case_argument.argument_type} {self.court_case_argument.number} {self.evidence_letter} ({self.order})"
    
    
class CourtCaseArgumentVideo(models.Model):
    court_case_argument = models.ForeignKey(CourtCaseArgument, on_delete=models.CASCADE, related_name='videos')
    youtube_url = models.URLField()
    evidence_letter = models.CharField(max_length=1)
    order = models.PositiveIntegerField(default=0, help_text="Order in which videos should be displayed")
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Case {self.court_case_argument.court_case.case_number}: {self.court_case_argument.argument_type} {self.court_case_argument.number} {self.evidence_letter} ({self.order})"

    def get_embed_url(self):
        import re
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', self.youtube_url)
        if match:
            return f"https://www.youtube.com/embed/{match.group(1)}"
        return None