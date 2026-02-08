from django.shortcuts import render
from django.db.models import Prefetch
from ..models import AternosGame
from collections import defaultdict

def aternos_games(request):
    games = AternosGame.objects.prefetch_related(
        "events__stages",
        "events__participants__nation",
        "events__participants__point_results",
        "events__participants__time_results",
        "events__participants__tournament_results",
    )
    
    # Process tournament events to group participants into matchups
    for game in games:
        for event in game.events.all():
            if event.event_type == "TOURNAMENT":
                stages_list = list(event.stages.all())
                
                # Rename stages for tournament display
                for idx, stage in enumerate(stages_list):
                    if idx == len(stages_list) - 1:
                        stage.display_name = "Winner"
                    else:
                        stage.display_name = f"Round {idx + 1}"
                    
                    # Group by matchup_number
                    matchup_dict = defaultdict(list)
                    for r in stage.tournament_round_results.all():
                        if not r.eliminated:
                            matchup_dict[r.matchup_number].append(r)
                    
                    # Convert to sorted list of matchups
                    stage.matchups = [matchup_dict[k] for k in sorted(matchup_dict.keys())]

    return render(request, "aternos_games.html", {"games": games})