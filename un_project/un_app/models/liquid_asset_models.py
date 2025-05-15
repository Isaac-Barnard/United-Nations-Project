from django.db import models
#from .nation_models import Nation
#from .company_models import Company
#from .denomination_models import Denomination

class LiquidAssetContainer(models.Model):
    name = models.CharField(max_length=100)
    nation = models.ForeignKey('Nation', on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, blank=True)
    ordering = models.IntegerField(default=0)  # Field for manual ordering
    
    class Meta:
        # Ensure the combination of nation/company and item is unique
        constraints = [
            models.UniqueConstraint(fields=['nation', 'name'], name='unique_nation_asset'),
            models.UniqueConstraint(fields=['company', 'name'], name='unique_company_asset'),
            models.CheckConstraint(
                check=(
                    models.Q(nation__isnull=False, company__isnull=True) |
                    models.Q(nation__isnull=True, company__isnull=False)
                ),
                name='nation_or_company_asset_not_both'
            )
        ]

    def __str__(self):
        if self.nation:
            return f'{self.nation.abbreviation} - ({self.name})'
        elif self.company:
            return f'{self.company.abbreviation} - ({self.name})'
        return f'{self.name}'

# --------------------------------------------------------------------
class LiquidCount(models.Model):
    asset_container = models.ForeignKey(LiquidAssetContainer, on_delete=models.CASCADE, null=True, blank=True)
    denomination = models.ForeignKey('Denomination', on_delete=models.CASCADE)
    count = models.DecimalField(max_digits=20, decimal_places=3)  # Allows for 2 decimal places

    class Meta:
        # Ensure the combination of nation/company and item is unique
        constraints = [
            models.UniqueConstraint(fields=['asset_container', 'denomination'], name='unique_nation_asset_denomination'),
            models.UniqueConstraint(fields=['asset_container', 'denomination'], name='unique_company_asset_enomination'),
            models.UniqueConstraint(fields=['asset_container', 'denomination'], name='unique_asset_denomination'),
        ]

    def __str__(self):
        if self.asset_container.nation:
            return f'({self.asset_container}) - {self.denomination.name} x {self.count}'
        elif self.asset_container.company:
            return f'({self.asset_container}) - {self.denomination.name} x {self.count}'
        return f'{self.denomination.name} x {self.count}'