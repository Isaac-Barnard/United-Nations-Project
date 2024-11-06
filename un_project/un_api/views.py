from rest_framework.views import APIView
from rest_framework.response import Response
from un_app.models import Building  # adjust path as needed to import Building model

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
                "price": float(building.price),
                # Add other fields as needed
            }
            for building in buildings
        ]
        return Response(data)