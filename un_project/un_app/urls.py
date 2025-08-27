from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),  # Default home page
    path('financial-home', financial_home, name='financial_home'),
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
    path('input-building/', input_building, name='input_building'),
    path('general-building-info/', general_building_info, name='general_building_info'),
    path('general-territory-info/', general_territory_info, name='general_territory_info'),
    path('currency-converter/', currency_converter, name='currency_converter'),
    
    # Item Counter Url's
    path('item-counter/', item_counter, name='item_counter'),
    path('get-containers/', get_containers, name='get_containers'),
    path('handle-liquid-asset-update/', handle_liquid_asset_update, name='handle-liquid-asset-update'),
    path('handle-item-update/', handle_item_update, name='handle-item-update'),
]
