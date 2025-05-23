# Generated by Django 5.1.1 on 2024-10-09 03:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("un_app", "0020_item_alter_buildingevaluation_building_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="description",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="building",
            name="architectural_genius",
            field=models.BooleanField(
                default=False,
                help_text="Damage to structures in the Register of Architectural and Engineering Wonders of the World (RAEWW) will result in court suits or settlements for damages will be doubled",
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="architectural_style",
            field=models.CharField(
                blank=True,
                help_text="The architectural style of the building if it falls into one",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="completed",
            field=models.BooleanField(
                default=True,
                help_text="Whether or not the building is completed. False means the building is incomplete",
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="historic_site",
            field=models.BooleanField(
                default=False,
                help_text="Damage to structures in the Register of Historic and Cultural Structures (RHCS) is considered war crime",
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="main_builders",
            field=models.ManyToManyField(
                help_text="The builder/builders who constructed the majority of the building",
                related_name="main_builds",
                to="un_app.player",
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="mopq_award",
            field=models.CharField(
                blank=True,
                help_text="Medal of Papa Quinn (MoPQ) award for architecture or another MoPQ award related to a building. Damages to structures that have won a Medal of Papa Quinn in the register will be considered a war crime",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="name",
            field=models.CharField(
                help_text="Building name", max_length=100, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="owner",
            field=models.ForeignKey(
                help_text="The nation that owns the building as its sovereign territory",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_buildings",
                to="un_app.nation",
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="territory",
            field=models.ForeignKey(
                help_text="The name of the territory district that this building resides. This does not necessarily indicate owner",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="buildings",
                to="un_app.territory",
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="x_coordinate",
            field=models.CharField(
                help_text="The x-coordinate of roughly center of the build",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="y_level_ground",
            field=models.FloatField(
                help_text="The ground level of the building. Measured to the ground level, not lowest point of the building ie. basements or mines",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="y_level_high_pt",
            field=models.FloatField(
                help_text="The highest point of the building", null=True
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="year_completed",
            field=models.IntegerField(
                help_text="The year where construction began on the building", null=True
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="z_coordinate",
            field=models.CharField(
                help_text="The z-coordinate of roughly center of the build",
                max_length=50,
            ),
        ),
    ]
