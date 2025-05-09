# Generated by Django 5.1.1 on 2024-11-08 05:00

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("un_app", "0046_building_ownership_minus_partial_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="nation",
            name="total_building_asset_value",
            field=models.DecimalField(
                decimal_places=6, default=Decimal("0"), max_digits=20
            ),
        ),
        migrations.AddField(
            model_name="nation",
            name="total_item_asset_value",
            field=models.DecimalField(
                decimal_places=6, default=Decimal("0"), max_digits=20
            ),
        ),
        migrations.AddField(
            model_name="nation",
            name="total_liquid_asset_value",
            field=models.DecimalField(
                decimal_places=6, default=Decimal("0"), max_digits=20
            ),
        ),
    ]
