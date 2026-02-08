from django.db import migrations
from django.utils.text import slugify

def populate_slugs(apps, schema_editor):
    Resolution = apps.get_model('un_records_app', 'Resolution')
    for r in Resolution.objects.all():
        if not r.slug:
            r.slug = slugify(r.title)
            r.save()

class Migration(migrations.Migration):

    dependencies = [
        ('un_records_app', '0039_resolution_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs),
    ]
