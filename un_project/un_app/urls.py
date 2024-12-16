from django.urls import path, include
from .views import building_list, player_list, home, nation_balance_sheet, evaluate_buildings, evaluation_success, evaluate_items, company_balance_sheet, un_map, get_building_evaluations, get_item_evaluations, item_counter, get_containers

urlpatterns = [
    path('', home, name='home'),  # Default home page
    path('buildings/', building_list, name='building_list'),  # http://127.0.0.1:8000/buildings/
    path('players/', player_list, name='player_list'),        # http://127.0.0.1:8000/players/
    path('nation/<str:nation_abbreviation>/', nation_balance_sheet, name='nation_balance_sheet'),  # http://127.0.0.1:8000/nation/XYZ/
    path('company/<str:company_abbreviation>/', company_balance_sheet, name='company_balance_sheet'),  # http://127.0.0.1:8000/company/XYZ/
    path('evaluate-buildings/', evaluate_buildings, name='evaluate_buildings'),
    path('get_evaluations/<int:building_id>/', get_building_evaluations, name='get_building_evaluations'),
    path('evaluation-success/', evaluation_success, name='evaluation_success'),
    path('accounts/', include('django.contrib.auth.urls')),  # Include built-in auth URLs
    path('evaluate-items/', evaluate_items, name='evaluate_items'),
    path('get_item_evaluations/<int:item_id>/', get_item_evaluations, name='get_item_evaluations'),
    path('map/', un_map, name='un_map'),
    path('item-counter/', item_counter, name='item_counter'),
    path('get-containers/', get_containers, name='get_containers'),
]
