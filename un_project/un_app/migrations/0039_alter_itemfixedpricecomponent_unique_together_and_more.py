# Generated by Django 5.1.1 on 2024-10-16 23:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("un_app", "0038_alter_itemcount_unique_together_itemcount_company_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="itemfixedpricecomponent",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="itemfixedpricecomponent",
            name="percentage_of_item",
            field=models.DecimalField(
                blank=True,
                decimal_places=8,
                help_text="Percentage of the referenced item's price to use",
                max_digits=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="itemfixedpricecomponent",
            name="referenced_item",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="referenced_in_components",
                to="un_app.item",
            ),
        ),
        migrations.AlterField(
            model_name="itemfixedpricecomponent",
            name="denomination",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="un_app.denomination",
            ),
        ),
        migrations.AlterField(
            model_name="itemfixedpricecomponent",
            name="quantity",
            field=models.DecimalField(
                blank=True, decimal_places=8, max_digits=20, null=True
            ),
        ),
        migrations.AddConstraint(
            model_name="itemfixedpricecomponent",
            constraint=models.UniqueConstraint(
                fields=("item", "denomination", "referenced_item"),
                name="unique_price_component",
            ),
        ),
    ]