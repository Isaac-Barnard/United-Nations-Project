from django.urls import path
from .views import BuildingDataView

urlpatterns = [
    path('buildings/', BuildingDataView.as_view(), name='building-data'),
]