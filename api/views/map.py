from geojson import LineString, Point
from geomet import wkt
from geopy.distance import great_circle
from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers.map.route import InputRouteSerializer
from utils.double_gis.service import DoubleGisService


class AbstractRouteView(views.APIView):
    POINTS_COUNT = 8
    SPEED = 3 * 1000 / 60
    permission_classes = (AllowAny,)
    serializer_class = InputRouteSerializer
    api = DoubleGisService().get_api()

    def serialize_linestring(self, linestring):
        result = [
            {
                'longitude': position[0],
                'latitude': position[1]
            } for position in linestring['coordinates']
        ]
        return result

    def points_to_query(self, points):
        str_points = ['{} {}'.format(*point['coordinates']) for point in points]
        return ','.join(str_points)

    def estimate_walking_time(self, point1, point2):
        # Время в минутах
        return great_circle(point1['coordinates'], point2['coordinates']).meters / self.SPEED

    def get_search_polygon(self, start_point):
        coordinates = start_point['coordinates']
        point1 = Point((coordinates[0] - 0.02, coordinates[1] + 0.01))
        point2 = Point((coordinates[0] + 0.02, coordinates[1] - 0.01))
        return point1, point2

    def search_destination(self, start_point, type):
        point1, point2 = self.get_search_polygon(start_point)
        response = self.api.geo.search(
            q='Магазин',
            # point='{},{}'.format(*start_point['coordinates']),
            point1='{},{}'.format(*point1['coordinates']),
            point2='{},{}'.format(*point2['coordinates']),
            type='building,poi',
            fields='items.geometry.selection'
        )
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        return wkt.loads(response['result']['items'][0]['geometry']['selection'])

    def build_round_route(self, points):
        query_points = self.points_to_query(points)
        print(query_points)
        response = self.api.transport.calculate_directions(
            waypoints=query_points,
            edge_filter='pedestrian',
            routing_type='shortest'
        )
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        legs = response['result']['items'][0]['legs']
        linestrings = []
        for leg in legs:
            for step in leg['steps']:
                for edge in step['edges']:
                    linestrings.append(wkt.loads(edge['geometry']['selection']))
        # Первое и последнее ребро - это отметки нулевой длины
        final_linestring_positions = []
        for linestring in linestrings[:-1]:
            final_linestring_positions.extend(linestring['coordinates'][1:])
        return LineString(tuple(final_linestring_positions))

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_point = Point((serializer.data['longitude'], serializer.data['latitude']))
        end_point = self.search_destination(start_point, 'street,building')
        print(
            'Оценочное время прогулки {walking_time} минут.'
            .format(walking_time=round(self.estimate_walking_time(start_point, end_point), 2))
        )
        return Response(
            self.serialize_linestring(self.build_round_route((start_point, end_point, start_point)))
        )


class InvestigateRouteView(AbstractRouteView):
    SEARCH_STRING = ''


class FoodRouteView(AbstractRouteView):
    SEARCH_STRING = 'Еда'


class BarRouteView(AbstractRouteView):
    SEARCH_STRING = 'Бар'


class CultureRouteView(AbstractRouteView):
    SEARCH_STRING = 'Театр музей'


class RomanticRouteView(AbstractRouteView):
    SEARCH_STRING = 'Мост'


class RandomRouteView(AbstractRouteView):
    def search_destination(self, start_point, type):
        response = self.api.geo.search(
            point='{},{}'.format(*start_point['coordinates']),
            radius=250,
            type='building,poi',
            fields='items.geometry.selection'
        )
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        return wkt.loads(response['result']['items'][0]['geometry']['selection'])