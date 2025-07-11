from rest_framework import serializers
from .models import User, Inventory, Players_Online
import base64

class Base64Binary(serializers.Field):
    def to_representation(self, value):
        if value is None:
            return None
        return base64.b64encode(value).decode('utf-8')
    def to_internal_value(self, data):
        try:
            return base64.b64decode(data)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Invalid binary data")

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'uuid']

class UserSerializer(serializers.ModelSerializer):
    skin_image = Base64Binary()
    face_image = Base64Binary()
    class Meta:
        model = User
        fields = ['username', 'uuid', 'skin_data', 'skin_image', 'face_image', 'is_slim', 'x', 'y', 'z', 'dimension', 'health', 'lastdeathx', 'lastdeathy', 'lastdeathz', 'lastdeathdim', 'xplevel', 'xppercent']

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = [
            'inventory_id',
            'inventory_type_id',
            'slot',
            'item_id',
            'amount',
            'name',
            'custom_name',
            'enchantments',
            'book_title',
            'book_author',
            'arrow_effect',
            'trim_material',
            'trim_pattern'
        ]

class PlayersOnline(serializers.ModelSerializer):
    class Meta:
        model = Players_Online
        fields = ['n']