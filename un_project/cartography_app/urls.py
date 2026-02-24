from django.urls import path, include
from .views import *
from un_app.views import un_map

urlpatterns = [
    path('cartography-home', cartography_home, name='cartography_home'),
    path('map/', un_map, name='interactive_map'),
]