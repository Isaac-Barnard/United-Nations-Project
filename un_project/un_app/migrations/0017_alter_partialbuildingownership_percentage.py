# Generated by Django 5.1.1 on 2024-10-03 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("un_app", "0016_alter_partialbuildingownership_partial_owner_abbreviation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partialbuildingownership",
            name="percentage",
            field=models.IntegerField(),
        ),
    ]