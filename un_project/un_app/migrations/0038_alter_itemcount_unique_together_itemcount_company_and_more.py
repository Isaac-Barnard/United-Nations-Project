# Generated by Django 5.1.1 on 2024-10-16 04:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("un_app", "0037_alter_item_price_type_alter_itemevaluation_item"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="itemcount",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="itemcount",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="un_app.company",
            ),
        ),
        migrations.AlterField(
            model_name="itemcount",
            name="nation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="un_app.nation",
            ),
        ),
        migrations.AddConstraint(
            model_name="itemcount",
            constraint=models.UniqueConstraint(
                fields=("nation", "item"), name="unique_nation_item"
            ),
        ),
        migrations.AddConstraint(
            model_name="itemcount",
            constraint=models.UniqueConstraint(
                fields=("company", "item"), name="unique_company_item"
            ),
        ),
        migrations.AddConstraint(
            model_name="itemcount",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("company__isnull", True), ("nation__isnull", False)),
                    models.Q(("company__isnull", False), ("nation__isnull", True)),
                    _connector="OR",
                ),
                name="nation_or_company_not_both",
            ),
        ),
    ]