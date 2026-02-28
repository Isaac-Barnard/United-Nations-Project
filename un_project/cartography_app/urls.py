from django.urls import path, include
from .views import *
# from un_app.views import un_map

urlpatterns = [
    path('cartography-home', cartography_home, name='cartography_home'),
    path('interactive-map/', interactive_un_map, name='interactive_un_map'),
    path('history-maps/', history_maps, name='history_maps'),
]