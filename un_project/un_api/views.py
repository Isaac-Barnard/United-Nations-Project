from rest_framework.views import APIView
from rest_framework.response import Response
from un_app.models import Building
from un_app.templatetags.custom_filters import custom_decimal_places

class BuildingDataView(APIView):
    def get(self, request):
        buildings = Building.objects.all()
        data = [
            {
                "name": building.name,
                "x_coordinate": float(building.x_coordinate),
                "z_coordinate": float(building.z_coordinate),
                "height": building.height,
                "owner": building.owner.name,
                "owner_abbreviation": building.owner.abbreviation,
                "price": custom_decimal_places(building.price),
                "builders": [builder.username for builder in building.main_builders.all()],
                # Add other fields as needed
            }
            for building in buildings
        ]
        return Response(data)