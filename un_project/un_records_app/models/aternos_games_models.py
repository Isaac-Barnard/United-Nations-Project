from django.db import models
from django.forms import ValidationError
from un_app.models import Nation, Player

class AternosGame(models.Model):
    name = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    participating_nations = models.ManyToManyField(Nation, blank=True, related_name='aternos_game')
    
    def __str__(self):
        return f"{self.name}"


class GameEvent(models.Model):
    EVENT_TYPES = [
        ("POINTS", "Points"),
        ("TIME", "Timed"),
        ("TOURNAMENT", "Tournament"),
    ]
    game = models.ForeignKey(AternosGame, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()})"
    
    
class EventParticipation(models.Model):
    event = models.ForeignKey(GameEvent, on_delete=models.CASCADE, related_name='participants')
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
    player_name = models.CharField(max_length=255)  # Minecraft username or player ID

    # Optional: generic placement field for all events
    final_placement = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('event', 'nation')

    def __str__(self):
        return f"{self.nation.name} in {self.event}"
    
    
class EventStage(models.Model):
    event = models.ForeignKey(GameEvent, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=255)  # "25 Block Race", "50 Block Race", "Round 1"
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.event.name} - {self.name}"
    
    class Meta:
        ordering = ['order'] 
    
# --------------------------------------------------------------------
    
class PointResult(models.Model):
    participant = models.ForeignKey(EventParticipation, on_delete=models.CASCADE, related_name="point_results")
    stage = models.ForeignKey(EventStage, on_delete=models.CASCADE, related_name="point_results")
    points = models.PositiveIntegerField()
    disqualified = models.BooleanField(default=False)

    def clean(self):
        if self.participant.event.event_type != "POINTS":
            raise ValidationError("This event does not use point scoring.")
    
    def __str__(self):
        return f"{self.participant} - {self.points} pts"


class TimeResult(models.Model):
    participant = models.ForeignKey(EventParticipation, on_delete=models.CASCADE, related_name="time_results")
    stage = models.ForeignKey(EventStage, on_delete=models.CASCADE, related_name="time_results")
    time_seconds = models.FloatField()
    disqualified = models.BooleanField(default=False)
    
    def clean(self):
        if self.participant.event.event_type != "TIME":
            raise ValidationError("This event is not a timed race.")

    def __str__(self):
        return f"{self.participant} - {self.time_seconds}s"


class TournamentRoundResult(models.Model):
    participant = models.ForeignKey(EventParticipation, on_delete=models.CASCADE, related_name="tournament_results")
    stage = models.ForeignKey(EventStage, on_delete=models.CASCADE, related_name="tournament_round_results")
    eliminated = models.BooleanField(default=False)
    disqualified = models.BooleanField(default=False)
    matchup_number = models.PositiveIntegerField(default=0, help_text="Which matchup in this stage (1, 2, 3, etc.)")
    
    class Meta:
        ordering = ['matchup_number', 'id']
    
    def clean(self):
        if self.participant.event.event_type != "TOURNAMENT":
            raise ValidationError("This event is not a tournament-style event.")

    def __str__(self):
        return f"{self.participant}, eliminated={self.eliminated}"