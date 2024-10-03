from django.urls import path
from .views import building_list, player_list, home, nation_building_list

urlpatterns = [
    path('', home, name='home'),  # Default home page
    path('buildings/', building_list, name='building_list'),  # http://127.0.0.1:8000/buildings/
    path('players/', player_list, name='player_list'),        # http://127.0.0.1:8000/players/
    path('nation/<str:nation_abbreviation>/', nation_building_list, name='nation_building_list'),  # http://127.0.0.1:8000/nation/XYZ/
]
