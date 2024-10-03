from django.urls import path
from .views import building_list, player_list, home

urlpatterns = [
    path('', home, name='home'),  # Default home page
    path('buildings/', building_list, name='building_list'),  # http://127.0.0.1:8000/buildings/
    path('players/', player_list, name='player_list')         # http://127.0.0.1:8000/players/
]
