from django import forms
from .models import Building, Denomination, Item


class BuildingEvaluationForm(forms.Form):
    building = forms.ModelChoiceField(queryset=Building.objects.all(), label='Select Building')
    
    def __init__(self, *args, **kwargs):
        super(BuildingEvaluationForm, self).__init__(*args, **kwargs)
        
        # Dynamically add a DecimalField for each denomination
        denominations = Denomination.objects.all()
        for denomination in denominations:
            field_name = f'denomination_{denomination.id}'
            self.fields[field_name] = forms.DecimalField(
                max_digits=20, decimal_places=8, min_value=0, required=False,
                label=f'{denomination.name} Quantity', initial=0
            )


class ItemEvaluationForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(price_type='market'), label='Select Item')
    
    def __init__(self, *args, **kwargs):
        super(ItemEvaluationForm, self).__init__(*args, **kwargs)
        
        # Dynamically add a DecimalField for each denomination
        denominations = Denomination.objects.all()
        for denomination in denominations:
            field_name = f'denomination_{denomination.id}'
            self.fields[field_name] = forms.DecimalField(
                max_digits=20, decimal_places=8, min_value=0, required=False,
                label=f'{denomination.name} Quantity', initial=0
            )
