# Generated by Django 5.1.1 on 2024-11-11 18:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("un_app", "0048_company_total_building_asset_value_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="LiquidAssetContainer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("ordering", models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveConstraint(
            model_name="liquidcount",
            name="nation_or_company_liquid_not_both",
        ),
        migrations.RemoveConstraint(
            model_name="liquidcount",
            name="unique_nation_asset_denomination",
        ),
        migrations.RemoveConstraint(
            model_name="liquidcount",
            name="unique_company_asset",
        ),
        migrations.RemoveField(
            model_name="liquidcount",
            name="asset_name",
        ),
        migrations.RemoveField(
            model_name="liquidcount",
            name="company",
        ),
        migrations.RemoveField(
            model_name="liquidcount",
            name="nation",
        ),
        migrations.AlterUniqueTogether(
            name="buildingevaluationcomponent",
            unique_together={("evaluation", "denomination")},
        ),
        migrations.AlterUniqueTogether(
            name="itemevaluationcomponent",
            unique_together={("evaluation", "denomination")},
        ),
        migrations.AddField(
            model_name="liquidassetcontainer",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="un_app.company",
            ),
        ),
        migrations.AddField(
            model_name="liquidassetcontainer",
            name="nation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="un_app.nation",
            ),
        ),
        migrations.AddField(
            model_name="liquidcount",
            name="asset_container",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="un_app.liquidassetcontainer",
            ),
        ),
        migrations.AddConstraint(
            model_name="liquidcount",
            constraint=models.UniqueConstraint(
                fields=("asset_container", "denomination"),
                name="unique_nation_asset_denomination",
            ),
        ),
        migrations.AddConstraint(
            model_name="liquidcount",
            constraint=models.UniqueConstraint(
                fields=("asset_container", "denomination"),
                name="unique_company_asset_enomination",
            ),
        ),
        migrations.AddConstraint(
            model_name="liquidassetcontainer",
            constraint=models.UniqueConstraint(
                fields=("nation", "name"), name="unique_nation_asset"
            ),
        ),
        migrations.AddConstraint(
            model_name="liquidassetcontainer",
            constraint=models.UniqueConstraint(
                fields=("company", "name"), name="unique_company_asset"
            ),
        ),
        migrations.AddConstraint(
            model_name="liquidassetcontainer",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("company__isnull", True), ("nation__isnull", False)),
                    models.Q(("company__isnull", False), ("nation__isnull", True)),
                    _connector="OR",
                ),
                name="nation_or_company_asset_not_both",
            ),
        ),
    ]
