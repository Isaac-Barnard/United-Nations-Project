from django.contrib import admin
from . import models

admin.site.register(models.ExecutiveOrder)
admin.site.register(models.ResolutionAmendment)
admin.site.register(models.Charter)
admin.site.register(models.CharterAmendment)
admin.site.register(models.DeclarationOfWar)
admin.site.register(models.NationalConstitution)
admin.site.register(models.NationalConstitutionAmendment)
admin.site.register(models.CourtCase)

class ResolutionImageInline(admin.TabularInline):
    model = models.ResolutionImage
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Resolution)
class ResolutionAdmin(admin.ModelAdmin):
    inlines = [ResolutionImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.ResolutionImage)
class ResolutionImageAdmin(admin.ModelAdmin):
    search_fields = ['resolution__title']
    ordering = ['resolution', 'order']
    

# --------------------------------------------------------------------
    
class TreatyImageInline(admin.TabularInline):
    model = models.TreatyImage
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Treaty)
class TreatyAdmin(admin.ModelAdmin):
    inlines = [TreatyImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.TreatyImage)
class TreatyImageAdmin(admin.ModelAdmin):
    search_fields = ['treaty__title']
    ordering = ['treaty', 'order']
    
    
# --------------------------------------------------------------------

class AllianceImageInline(admin.TabularInline):
    model = models.AllianceImage
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Alliance)
class AllianceAdmin(admin.ModelAdmin):
    inlines = [AllianceImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.AllianceImage)
class AllianceImageAdmin(admin.ModelAdmin):
    search_fields = ['alliance__title']
    ordering = ['alliance', 'order']
    
    
# --------------------------------------------------------------------

class PetitionImageInline(admin.TabularInline):
    model = models.PetitionImage
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Petition)
class PetitionAdmin(admin.ModelAdmin):
    inlines = [PetitionImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.PetitionImage)
class PetitionImageAdmin(admin.ModelAdmin):
    search_fields = ['petition__title']
    ordering = ['petition', 'order']
    
    
# --------------------------------------------------------------------

class CourtCaseArgumentImageInline(admin.TabularInline):
    model = models.CourtCaseArgumentImage
    extra = 2
    fields = ['image', 'order', 'evidence_letter', 'description']
    ordering = ['order']
    
class CourtCaseArgumentVideoInline(admin.TabularInline):
    model = models.CourtCaseArgumentVideo
    extra = 1
    fields = ['youtube_url', 'order', 'evidence_letter', 'description']
    ordering = ['order']

@admin.register(models.CourtCaseArgument)
class CourtCaseArgumentAdmin(admin.ModelAdmin):
    inlines = [CourtCaseArgumentImageInline, CourtCaseArgumentVideoInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.CourtCaseArgumentImage)
class CourtCaseArgumentImageAdmin(admin.ModelAdmin):
    search_fields = ['court_case_argument__title']
    ordering = ['court_case_argument', 'order']
    

# --------------------------------------------------------------------
    
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


# These inlines need to specify that they're related through 'stage', not directly to GameEvent
class TimeResultInline(admin.TabularInline):
    model = models.TimeResult
    extra = 0
    fk_name = 'stage'  # Tell Django to use the 'stage' FK, not look for a direct GameEvent FK
    fields = ['participant', 'time_seconds', 'disqualified']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "participant":
            # Extract event_id from the URL (for EventStage admin page)
            if hasattr(self, 'parent_obj') and self.parent_obj:
                kwargs["queryset"] = models.EventParticipation.objects.filter(event=self.parent_obj.event)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class PointResultInline(admin.TabularInline):
    model = models.PointResult
    extra = 0
    fk_name = 'stage'
    fields = ['participant', 'points', 'disqualified']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "participant":
            if hasattr(self, 'parent_obj') and self.parent_obj:
                kwargs["queryset"] = models.EventParticipation.objects.filter(event=self.parent_obj.event)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class TournamentRoundResultInline(admin.TabularInline):
    model = models.TournamentRoundResult
    extra = 1
    fk_name = 'stage'
    fields = ['participant', 'eliminated', 'disqualified']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "participant":
            if hasattr(self, 'parent_obj') and self.parent_obj:
                kwargs["queryset"] = models.EventParticipation.objects.filter(event=self.parent_obj.event)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.GameEvent)
class GameEventAdmin(admin.ModelAdmin):
    fields = ['game', 'name', 'event_type']
    list_display = ['name', 'game', 'event_type']
    list_filter = ['event_type', 'game']
    inlines = [EventStageInline, EventParticipationInline]


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
    
    def get_inline_instances(self, request, obj=None):
        """Dynamically show the correct result inline based on event type."""
        inline_instances = []
        
        if obj and obj.event:
            # Store the parent object for use in formfield_for_foreignkey
            if obj.event.event_type == 'TIME':
                inline = TimeResultInline(self.model, self.admin_site)
                inline.parent_obj = obj
                inline_instances.append(inline)
            elif obj.event.event_type == 'POINTS':
                inline = PointResultInline(self.model, self.admin_site)
                inline.parent_obj = obj
                inline_instances.append(inline)
            elif obj.event.event_type == 'TOURNAMENT':
                inline = TournamentRoundResultInline(self.model, self.admin_site)
                inline.parent_obj = obj
                inline_instances.append(inline)
        
        return inline_instances

@admin.register(models.EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ['event', 'nation', 'player_name', 'final_placement']
    search_fields = ['player_name', 'nation__name', 'event__name']
    list_filter = ['event']

admin.site.register(models.TimeResult)
admin.site.register(models.PointResult)
admin.site.register(models.TournamentRoundResult)