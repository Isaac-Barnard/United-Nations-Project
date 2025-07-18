# Generated by Django 5.2.1 on 2025-06-27 02:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('un_app', '0059_rename_year_completed_building_year_started'),
        ('un_records_app', '0018_declaration_of_war_resolving_treaty'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AllianceImage',
            new_name='Alliance_Image',
        ),
        migrations.RenameModel(
            old_name='CharterAmendment',
            new_name='Charter_Amendment',
        ),
        migrations.RenameModel(
            old_name='ResolutionAmendment',
            new_name='Resolution_Amendment',
        ),
        migrations.RenameModel(
            old_name='ResolutionImage',
            new_name='Resolution_Image',
        ),
        migrations.RenameModel(
            old_name='TreatyImage',
            new_name='Treaty_Image',
        ),
        migrations.CreateModel(
            name='National_Constitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('body', models.TextField()),
                ('void', models.BooleanField(blank=True, default=False)),
                ('invalidation_date', models.DateField(blank=True, default=None, help_text="Date the nation's constitution was considered void or repealed", null=True)),
                ('nation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nation_constitution', to='un_app.nation')),
            ],
        ),
        migrations.CreateModel(
            name='National_Constitution_Amendment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('body', models.TextField()),
                ('void', models.BooleanField(blank=True, default=False)),
                ('invalidation_date', models.DateField(blank=True, default=None, help_text='Date the amendment was considered void or repealed', null=True)),
                ('national_constitution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amended_national_constitution', to='un_records_app.national_constitution')),
            ],
        ),
    ]
