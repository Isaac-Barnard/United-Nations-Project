# Generated by Django 5.1.1 on 2024-10-02 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("un_app", "0010_alter_building_y_level_ground_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="building",
            name="year_completed",
            field=models.IntegerField(null=True),
        ),
    ]