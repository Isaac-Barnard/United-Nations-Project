from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import BuildingEvaluationForm
from ..models import Denomination, UserProfile, BuildingEvaluation, BuildingEvaluationComponent
from django.http import JsonResponse

def calculate_total_diamond_value(form_data, denominations):
    """Helper function to calculate total diamond value"""
    total_diamond_value = 0
    for denomination in denominations:
        field_name = f'denomination_{denomination.id}'
        quantity = form_data.get(field_name, 0)
        if isinstance(quantity, str):
            try:
                quantity = float(quantity)
            except ValueError:
                quantity = 0
        total_diamond_value += quantity * denomination.diamond_equivalent
    return total_diamond_value

@login_required
def evaluate_buildings(request):
    # Fetch the denominations to pass to the template
    denominations = Denomination.objects.all().order_by('priority')
    selected_building = None
    evaluation_data = []
    
    if request.method == 'POST':
        evaluation_form = BuildingEvaluationForm(request.POST)
        if evaluation_form.is_valid():

            selected_building = evaluation_form.cleaned_data['building']  # Get the selected building
            evaluator = request.user

            # Check if evaluator has a related UserProfile and Player instance
            try:
                evaluator_profile = evaluator.userprofile  # Access UserProfile related to User
                evaluator_player = evaluator_profile.player  # Get the associated Player
            except UserProfile.DoesNotExist:
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'Your account is not set up correctly.'
                })

            # Check if the evaluator is authorized (un_rep=True)
            if not evaluator_player.un_rep:
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'You do not have permission to evaluate buildings.'
                })
            
            # Calculate total diamond value
            total_diamond_value = calculate_total_diamond_value(evaluation_form.cleaned_data, denominations)
            
            # Check if the evaluation is greater than 0
            if total_diamond_value <= 0:
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,
                    'error_message': 'The evaluation must be greater than 0.'
                })

            # Fetch existing evaluations for the selected building
            evaluations = BuildingEvaluation.objects.filter(building=selected_building).select_related('evaluator').prefetch_related('evaluation_components')

            for evaluation in evaluations:
                evaluator_name = evaluation.evaluator.username
                component_data = {denom.id: 0 for denom in denominations}  # Initialize all to 0
                
                for component in evaluation.evaluation_components.all():
                    component_data[component.denomination.id] = component.quantity  # Update with actual values

                evaluation_data.append({
                    'evaluator': evaluator_name,
                    'components': component_data
                })

            # Check if evaluator has already evaluated this building
            if BuildingEvaluation.objects.filter(building=selected_building, evaluator=evaluator_player).exists():
                return render(request, 'evaluate_buildings.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,
                    'error_message': 'You have already evaluated this building.'
                })

            # Create BuildingEvaluation
            building_evaluation = BuildingEvaluation.objects.create(
                building=selected_building,
                evaluator=evaluator_player
            )

            # Iterate over denomination fields and create BuildingEvaluationComponents
            for denomination in denominations:
                field_name = f'denomination_{denomination.id}'
                quantity = evaluation_form.cleaned_data.get(field_name, 0)
                if quantity > 0:
                    BuildingEvaluationComponent.objects.create(
                        evaluation=building_evaluation,
                        denomination=denomination,
                        quantity=quantity
                    )

            return redirect('evaluation_success')

    else:
        evaluation_form = BuildingEvaluationForm()

    # Always pass the denominations to the template
    return render(request, 'evaluate_buildings.html', {
        'evaluation_form': evaluation_form,
        'denominations': denominations,
        'selected_building': selected_building,
        'evaluation_data': evaluation_data,  # Pass evaluations to the template
    })

@login_required
def get_building_evaluations(request, building_id):
    denominations = Denomination.objects.all().order_by('priority')
    evaluations = BuildingEvaluation.objects.filter(building_id=building_id).select_related('evaluator').prefetch_related('evaluation_components')
    evaluation_data = []

    for evaluation in evaluations:
        evaluator_name = evaluation.evaluator.username
        component_data = {denom.name: 0 for denom in denominations}  # Initialize with denomination names

        for component in evaluation.evaluation_components.all():
            component_data[component.denomination.name] = float(component.quantity)  # Use denomination name

        evaluation_data.append({
            'evaluator': evaluator_name,
            'components': component_data,
            'total_diamond_value': float(evaluation.total_diamond_value)
        })

    return JsonResponse({
        'denominations': [denom.name for denom in denominations],
        'evaluation_data': evaluation_data
    })