from django import forms
from .models import Building, Denomination


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