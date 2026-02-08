from django.db import migrations
from django.utils.text import slugify

def populate_slugs(apps, schema_editor):
    Treaty = apps.get_model('un_records_app', 'CourtCase')
    for r in Treaty.objects.all():
        if not r.slug:
            r.slug = slugify(r.title)
            r.save()

class Migration(migrations.Migration):

    dependencies = [
        ('un_records_app', '0045_courtcase_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs),
    ]
