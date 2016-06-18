from geojson import Point
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers.map.route import InputRouteSerializer
from utils.double_gis.geometry import Parser
from utils.double_gis.service import DoubleGisService


class AbstractRouteView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = InputRouteSerializer
    api = DoubleGisService().get_api()
    parser = Parser()

    def points_to_query(self, points):
        str_points = ['{} {}'.format(*point['coordinates']) for point in points]
        return ','.join(str_points)


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


class RandomRouteView(AbstractRouteView):
    permission_classes = (AllowAny,)
    serializer_class = InputRouteSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_point = Point((serializer.data['longitude'], serializer.data['latitude']))
        response = self.api.geo.search(
            point='{},{}'.format(*start_point['coordinates']),
            radius=250,
            type='building,poi',
            page_size=1,
            fields='items.geometry.selection'
        )
        item = response['result']['items'][0]['geometry']['selection']
        end_point = self.parser.parse_point(item)
        query_points = self.points_to_query((start_point, end_point))
        response = self.api.transport.calculate_directions(
            waypoints=query_points,
            edge_filter='pedestrian',
            routing_type='shortest'
        )
        legs = response['result']['items'][0]['legs']
        linestrings = []
        for leg in legs:
            for step in leg['steps']:
                for edge in step['edges']:
                    linestrings.append(self.parser.parse(edge['geometry']['selection']))
        # Первое и последнее ребро - это отметки нулевой длины
        final_linestring_positions = []
        for linestring in linestrings[:-1]:
            final_linestring_positions.append(linestring['coordinates'][0])
        return Response(response)
