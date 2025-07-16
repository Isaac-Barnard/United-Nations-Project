from django.urls import path, include
from .views import *

urlpatterns = [
    path('records-home', records_home, name='records_home'),
    path('charter', charter, name='charter'),
    path('resolutions', resolutions, name='resolutions'),
    path('court-cases', court_cases, name='court_cases'),
    path('treaties', treaties, name='treaties'),
    path('executive_orders', executive_orders, name='executive_orders'),
    path('alliances', alliances, name='alliances'),
    path('declaration_of_wars', declaration_of_wars, name='declaration_of_wars'),
    path('national_constitution', national_constitutions, name='national_constitution'),
    path('petitions', petitions, name='petitions'),
]