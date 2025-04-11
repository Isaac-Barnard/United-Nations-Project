from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserList.as_view(), name='user-list'),
    path('user/<str:username>/', views.UserView.as_view(), name='user-data'),
    path('inventory/<str:username>/', views.InventoryView.as_view(), name='inv-data'),
    path('players/', views.PlayersOnline.as_view(), name='players-online')
]