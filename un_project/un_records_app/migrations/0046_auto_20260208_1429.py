from django.db import migrations
from django.utils.text import slugify

def populate_courtcase_slugs(apps, schema_editor):
    CourtCase = apps.get_model('un_records_app', 'CourtCase')
    existing_slugs = set(CourtCase.objects.values_list('slug', flat=True))

    for case in CourtCase.objects.all():
        # Generate a base slug
        base_slug = f"case-{case.case_number}"
        slug = slugify(base_slug)
        original_slug = slug
        counter = 1

        # Ensure uniqueness
        while slug in existing_slugs:
            counter += 1
            slug = f"{original_slug}-{counter}"

        # Update slug and track it
        case.slug = slug
        case.save()
        existing_slugs.add(slug)

class Migration(migrations.Migration):

    dependencies = [
        ('un_records_app', '0045_courtcase_slug'),
    ]

    operations = [
        migrations.RunPython(populate_courtcase_slugs),
    ]
