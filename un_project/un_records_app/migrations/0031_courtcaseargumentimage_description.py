# Generated by Django 5.2.4 on 2025-07-10 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('un_records_app', '0030_alter_courtcase_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='courtcaseargumentimage',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
