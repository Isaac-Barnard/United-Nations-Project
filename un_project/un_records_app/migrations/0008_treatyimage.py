# Generated by Django 5.2.1 on 2025-06-10 01:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('un_records_app', '0007_resolutionimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreatyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='treaty_images/')),
                ('order', models.PositiveIntegerField(default=0, help_text='Order in which images should be displayed')),
                ('treaty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='un_records_app.treaty')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
