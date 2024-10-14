from django.urls import path, include
from .views import building_list, player_list, home, nation_balance_sheet, evaluate_buildings, evaluation_success, evaluate_items

urlpatterns = [
    path('', home, name='home'),  # Default home page
    path('buildings/', building_list, name='building_list'),  # http://127.0.0.1:8000/buildings/
    path('players/', player_list, name='player_list'),        # http://127.0.0.1:8000/players/
    path('nation/<str:nation_abbreviation>/', nation_balance_sheet, name='nation_balance_sheet'),  # http://127.0.0.1:8000/nation/XYZ/
    path('evaluate-buildings/', evaluate_buildings, name='evaluate_buildings'),
    path('evaluation-success/', evaluation_success, name='evaluation_success'),
    path('accounts/', include('django.contrib.auth.urls')),  # Include built-in auth URLs
    path('evaluate-items/', evaluate_items, name='evaluate_items'),
]
