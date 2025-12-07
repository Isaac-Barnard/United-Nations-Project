from django.contrib import admin
from .. import models
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.forms import modelformset_factory
from django.contrib import messages
from django.db import transaction

# Basic inlines for GameEvent
class EventStageInline(admin.TabularInline):
    model = models.EventStage
    extra = 1
    fields = ['name', 'order']
    ordering = ['order']

class EventParticipationInline(admin.TabularInline):
    model = models.EventParticipation
    extra = 1
    fields = ['nation', 'player_name', 'final_placement']
    autocomplete_fields = ['nation']


@admin.register(models.GameEvent)
class GameEventAdmin(admin.ModelAdmin):
    fields = ['game', 'name', 'event_type']
    list_display = ['name', 'game', 'event_type', 'manage_results_link']
    list_filter = ['event_type', 'game']
    inlines = [EventStageInline, EventParticipationInline]
    
    def manage_results_link(self, obj):
        from django.utils.html import format_html
        url = reverse('admin:manage_event_results', args=[obj.pk])
        return format_html('<a href="{}">Manage Results</a>', url)
    manage_results_link.short_description = 'Results'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/manage-results/',
                self.admin_site.admin_view(self.manage_results_view),
                name='manage_event_results',
            ),
            path(
                '<path:object_id>/save-results/',
                self.admin_site.admin_view(self.save_results_view),
                name='save_event_results',
            ),
        ]
        return custom_urls + urls
    
    def manage_results_view(self, request, object_id):
        event = get_object_or_404(models.GameEvent, pk=object_id)
        stages = event.stages.all().order_by('order')
        participants = event.participants.all()
        
        # Create a list structure for easier template access
        participant_results = []
        
        for participant in participants:
            stage_results = []
            for stage in stages:
                result_data = {
                    'participant_id': participant.id,
                    'stage_id': stage.id,
                    'value': '',
                    'disqualified': False,
                    'eliminated': False,
                    'matchup_number': 1  # Default matchup number
                }
                stage_results.append(result_data)
            
            participant_results.append({
                'participant': participant,
                'stage_results': stage_results
            })
        
        # Fetch existing results based on event type and populate the data
        if event.event_type == 'POINTS':
            existing_results = models.PointResult.objects.filter(
                participant__event=event
            ).select_related('participant', 'stage')
            for result in existing_results:
                # Find and update the correct result in our structure
                for p_data in participant_results:
                    if p_data['participant'].id == result.participant.id:
                        for s_result in p_data['stage_results']:
                            if s_result['stage_id'] == result.stage.id:
                                s_result['value'] = result.points
                                s_result['disqualified'] = result.disqualified
                                break
                        break
                        
        elif event.event_type == 'TIME':
            existing_results = models.TimeResult.objects.filter(
                participant__event=event
            ).select_related('participant', 'stage')
            for result in existing_results:
                for p_data in participant_results:
                    if p_data['participant'].id == result.participant.id:
                        for s_result in p_data['stage_results']:
                            if s_result['stage_id'] == result.stage.id:
                                s_result['value'] = result.time_seconds
                                s_result['disqualified'] = result.disqualified
                                break
                        break
                        
        elif event.event_type == 'TOURNAMENT':
            existing_results = models.TournamentRoundResult.objects.filter(
                participant__event=event
            ).select_related('participant', 'stage')
            for result in existing_results:
                for p_data in participant_results:
                    if p_data['participant'].id == result.participant.id:
                        for s_result in p_data['stage_results']:
                            if s_result['stage_id'] == result.stage.id:
                                s_result['value'] = 'eliminated' if result.eliminated else 'active'
                                s_result['disqualified'] = result.disqualified
                                s_result['eliminated'] = result.eliminated
                                s_result['matchup_number'] = result.matchup_number
                                break
                        break
        
        context = {
            'event': event,
            'stages': stages,
            'participant_results': participant_results,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
            'has_change_permission': self.has_change_permission(request, event),
        }
        
        return render(request, 'admin/manage_event_results.html', context)
    
    def save_results_view(self, request, object_id):
        if request.method != 'POST':
            return redirect('admin:manage_event_results', object_id=object_id)
        
        event = get_object_or_404(models.GameEvent, pk=object_id)
        
        with transaction.atomic():
            # Process each result from the form
            for key, value in request.POST.items():
                if key.startswith('result_'):
                    # Parse: result_participantID_stageID
                    parts = key.split('_')
                    if len(parts) == 3:
                        participant_id = parts[1]
                        stage_id = parts[2]
                        
                        participant = models.EventParticipation.objects.get(id=participant_id)
                        stage = models.EventStage.objects.get(id=stage_id)
                        
                        disqualified_key = f'disqualified_{participant_id}_{stage_id}'
                        disqualified = disqualified_key in request.POST
                        
                        # Get matchup number for tournament events
                        matchup_key = f'matchup_{participant_id}_{stage_id}'
                        matchup_number = int(request.POST.get(matchup_key, 1))
                        
                        # Skip empty values
                        if not value or value.strip() == '':
                            # Delete existing result if clearing the value
                            if event.event_type == 'POINTS':
                                models.PointResult.objects.filter(
                                    participant=participant, stage=stage
                                ).delete()
                            elif event.event_type == 'TIME':
                                models.TimeResult.objects.filter(
                                    participant=participant, stage=stage
                                ).delete()
                            elif event.event_type == 'TOURNAMENT':
                                models.TournamentRoundResult.objects.filter(
                                    participant=participant, stage=stage
                                ).delete()
                            continue
                        
                        # Create or update based on event type
                        if event.event_type == 'POINTS':
                            models.PointResult.objects.update_or_create(
                                participant=participant,
                                stage=stage,
                                defaults={
                                    'points': int(value),
                                    'disqualified': disqualified
                                }
                            )
                        elif event.event_type == 'TIME':
                            models.TimeResult.objects.update_or_create(
                                participant=participant,
                                stage=stage,
                                defaults={
                                    'time_seconds': float(value),
                                    'disqualified': disqualified
                                }
                            )
                        elif event.event_type == 'TOURNAMENT':
                            eliminated = value == 'eliminated'
                            models.TournamentRoundResult.objects.update_or_create(
                                participant=participant,
                                stage=stage,
                                defaults={
                                    'eliminated': eliminated,
                                    'disqualified': disqualified,
                                    'matchup_number': matchup_number
                                }
                            )
        
        messages.success(request, 'Results saved successfully!')
        return redirect('admin:manage_event_results', object_id=object_id)


@admin.register(models.AternosGame)
class AternosGameAdmin(admin.ModelAdmin):
    list_display = ['name', 'year']
    search_fields = ['name']
    filter_horizontal = ['participating_nations']

@admin.register(models.EventStage)
class EventStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'order']
    ordering = ['event', 'order']
    search_fields = ['name', 'event__name']

@admin.register(models.EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ['event', 'nation', 'player_name', 'final_placement']
    search_fields = ['player_name', 'nation__name', 'event__name']
    list_filter = ['event']

admin.site.register(models.TimeResult)
admin.site.register(models.PointResult)
admin.site.register(models.TournamentRoundResult)