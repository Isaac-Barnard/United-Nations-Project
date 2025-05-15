from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import ItemEvaluationForm
from ..models import Denomination, UserProfile, ItemEvaluation, ItemEvaluationComponent
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
def evaluate_items(request):
    denominations = Denomination.objects.all().order_by('priority')
    selected_item = None
    evaluation_data = []
    
    if request.method == 'POST':
        evaluation_form = ItemEvaluationForm(request.POST)
        if evaluation_form.is_valid():
            selected_item = evaluation_form.cleaned_data['item']
            evaluator = request.user

            # Check if evaluator has a related UserProfile and Player instance
            try:
                evaluator_profile = evaluator.userprofile  # Access UserProfile related to User
                evaluator_player = evaluator_profile.player  # Get the associated Player
            except UserProfile.DoesNotExist:
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'Your account is not set up correctly.'
                })

            # Check if the evaluator is authorized (un_rep=True)
            if not evaluator_player.un_rep:
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'You do not have permission to evaluate items.'
                })
            
            # Calculate total diamond value
            total_diamond_value = calculate_total_diamond_value(evaluation_form.cleaned_data, denominations)
            
            # Check if the evaluation is greater than 0
            if total_diamond_value <= 0:
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,
                    'error_message': 'The evaluation must be greater than 0.'
                })

            # Get item
            item = evaluation_form.cleaned_data['item']

            # Check if evaluator has already evaluated this item
            if ItemEvaluation.objects.filter(item=item, evaluator=evaluator_player).exists():
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,  # Ensure denominations are passed in case of error
                    'error_message': 'You have already evaluated this item.'
                })
            
            evaluations = ItemEvaluation.objects.filter(item=selected_item).select_related('evaluator').prefetch_related('evaluation_components')

            for evaluation in evaluations:
                evaluator_name = evaluation.evaluator.username
                component_data = {denom.id: 0 for denom in denominations}
                
                for component in evaluation.evaluation_components.all():
                    component_data[component.denomination.id] = component.quantity

                evaluation_data.append({
                    'evaluator': evaluator_name,
                    'components': component_data
                })

            if ItemEvaluation.objects.filter(item=selected_item, evaluator=evaluator_player).exists():
                return render(request, 'evaluate_items.html', {
                    'evaluation_form': evaluation_form,
                    'denominations': denominations,
                    'error_message': 'You have already evaluated this item.'
                })

            # Create ItemEvaluation
            item_evaluation = ItemEvaluation.objects.create(
                item=selected_item,
                evaluator=evaluator_player
            )

            # Iterate over denomination fields and create ItemEvaluationComponents
            for denomination in denominations:
                field_name = f'denomination_{denomination.id}'
                quantity = evaluation_form.cleaned_data.get(field_name, 0)
                if quantity > 0:
                    ItemEvaluationComponent.objects.create(
                        evaluation=item_evaluation,
                        denomination=denomination,
                        quantity=quantity
                    )

            return redirect('evaluation_success')

    else:
        evaluation_form = ItemEvaluationForm()

    # Always pass the denominations to the template
    return render(request, 'evaluate_items.html', {
        'evaluation_form': evaluation_form,
        'denominations': denominations,
        'selected_item': selected_item,
        'evaluation_data': evaluation_data,
    })

@login_required
def get_item_evaluations(request, item_id):
    denominations = Denomination.objects.all().order_by('priority')
    evaluations = ItemEvaluation.objects.filter(item_id=item_id).select_related('evaluator').prefetch_related('evaluation_components')
    evaluation_data = []

    for evaluation in evaluations:
        evaluator_name = evaluation.evaluator.username
        component_data = {denom.name: 0 for denom in denominations}

        for component in evaluation.evaluation_components.all():
            component_data[component.denomination.name] = float(component.quantity)

        evaluation_data.append({
            'evaluator': evaluator_name,
            'components': component_data,
            'total_diamond_value': float(evaluation.total_diamond_value)
        })

    return JsonResponse({
        'denominations': [denom.name for denom in denominations],
        'evaluation_data': evaluation_data
    })