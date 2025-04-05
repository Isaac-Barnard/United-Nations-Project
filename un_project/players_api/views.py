from django.shortcuts import render
from rest_framework import generics, views, response
from .models import User, Inventory, Players_Online
from .serializers import UserSerializer, UserListSerializer, InventorySerializer, PlayersOnline
# Create your views here.
class UserList(generics.ListAPIView):
    queryset = User.objects.values('username', 'uuid')
    serializer_class = UserListSerializer
class UserView(views.APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user)
            return response.Response(serializer.data)
        except User.DoesNotExist:
            return response.Response({"error": "User not found"}, status=404)
class InventoryView(views.APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            uuid = user.uuid
            inv = Inventory.objects.filter(uuid=uuid)
            serializer = InventorySerializer(inv, many=True)
            return response.Response(serializer.data)
        except User.DoesNotExist:
            return response.Response({"error": "User not found"}, status=404)
        except Inventory.DoesNotExist:
            return response.Response({"error": "No inventory data found"}, status=404)
class PlayersOnline(generics.ListAPIView):
    queryset = Players_Online.objects.values('n')
    serializer_class = PlayersOnline