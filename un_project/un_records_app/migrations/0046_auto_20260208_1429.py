from django.db import migrations
from django.utils.text import slugify

def populate_courtcase_slugs(apps, schema_editor):
    CourtCase = apps.get_model('un_records_app', 'CourtCase')
    for case in CourtCase.objects.all():
        if not case.slug:
            case.slug = f"case-{case.case_number}"
            case.save()

class Migration(migrations.Migration):

    dependencies = [
        ('un_records_app', '0045_courtcase_slug'),
    ]

    operations = [
        migrations.RunPython(populate_courtcase_slugs),
    ]
