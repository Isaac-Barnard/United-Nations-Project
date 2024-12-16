from django import forms
from .models import Building, Denomination, Item, Nation, LiquidAssetContainer, Company


class BuildingEvaluationForm(forms.Form):
    building = forms.ModelChoiceField(queryset=Building.objects.all(), label='Select Building')
    
    def __init__(self, *args, **kwargs):
        super(BuildingEvaluationForm, self).__init__(*args, **kwargs)
        
        # Dynamically add a DecimalField for each denomination
        denominations = Denomination.objects.all()
        special_names = {"Redstone Dust", "Lapis Lazuli", "Coal"}

        for denomination in denominations:
            field_name = f'denomination_{denomination.id}'
            label = f'{denomination.name}' if denomination.name in special_names else f'{denomination.name}s'
            self.fields[field_name] = forms.DecimalField(
                max_digits=20, decimal_places=8, min_value=0, required=False,
                label=label, initial=0
            )


class ItemEvaluationForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(price_type='market_rate'), label='Select Item')
    
    def __init__(self, *args, **kwargs):
        super(ItemEvaluationForm, self).__init__(*args, **kwargs)
        
        # Dynamically add a DecimalField for each denomination
        denominations = Denomination.objects.all()
        special_names = {"Redstone Dust", "Lapis Lazuli", "Coal"}

        for denomination in denominations:
            field_name = f'denomination_{denomination.id}'
            label = f'{denomination.name}' if denomination.name in special_names else f'{denomination.name}s'
            self.fields[field_name] = forms.DecimalField(
                max_digits=20, decimal_places=8, min_value=0, required=False,
                label=label, initial=0
            )


class ItemCounterForm(forms.Form):
    nation = forms.ModelChoiceField(
        queryset=Nation.objects.all(),
        empty_label="Select a Nation",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        empty_label="Select a Company",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    container = forms.ModelChoiceField(
        queryset=LiquidAssetContainer.objects.none(),
        empty_label="Select a Container",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    item = forms.ModelChoiceField(
        queryset=Item.objects.all().order_by('ordering'),
        empty_label="Select an Item",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    count = forms.DecimalField(
        max_digits=20,
        decimal_places=3,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'})
    )
    denomination = forms.ModelChoiceField(
        queryset=Denomination.objects.all().order_by('priority'),
        empty_label="Select a Denomination",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'nation' in kwargs['initial']:
                nation = kwargs['initial']['nation']
                self.fields['container'].queryset = LiquidAssetContainer.objects.filter(
                    nation=nation
                ).order_by('ordering')
            elif 'company' in kwargs['initial']:
                company = kwargs['initial']['company']
                self.fields['container'].queryset = LiquidAssetContainer.objects.filter(
                    company=company
                ).order_by('ordering')



class LiquidAssetForm(forms.Form):
    def __init__(self, denominations, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for denomination in denominations:
            self.fields[f'denomination_{denomination.id}'] = forms.DecimalField(
                max_digits=20,
                decimal_places=3,
                required=False,
                initial=0,
                min_value=0,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control input-cell',
                    'step': '0.001',
                    'data-diamond-equivalent': denomination.diamond_equivalent
                })
            )