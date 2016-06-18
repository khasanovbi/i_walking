import requests
from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers.map.route import InputRouteSerializer


class AbstractRouteView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = InputRouteSerializer


class InvestigateRouteView(AbstractRouteView):
    pass


class FoodRouteView(AbstractRouteView):
    pass


class BarRouteView(AbstractRouteView):
    pass


class CultureRouteView(AbstractRouteView):
    pass


class RomanticRouteView(AbstractRouteView):
    pass


class RandomRouteView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = InputRouteSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = requests.get(
            'http://catalog.api.2gis.ru/2.0/geo/search'
            '?point={longitude},{latitude}'
            '&type=street,building'
            '&radius={radius}'
            '&key={key}'
            .format(
                key=settings.DOUBLE_GIS_API_KEY,
                radius=250,
                longitude=serializer.data['longitude'],
                latitude=serializer.data['latitude']
            )
        )
        return Response(response.json())
