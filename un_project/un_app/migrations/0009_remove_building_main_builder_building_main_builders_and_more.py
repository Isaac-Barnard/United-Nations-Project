# Generated by Django 5.1.1 on 2024-10-02 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("un_app", "0008_alter_building_mopq_award"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="building",
            name="main_builder",
        ),
        migrations.AddField(
            model_name="building",
            name="main_builders",
            field=models.ManyToManyField(
                related_name="main_builds", to="un_app.player"
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="mopq_award",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
