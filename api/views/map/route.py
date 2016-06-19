from geojson import LineString, Point
from geomet import wkt
from geopy.distance import great_circle
from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers.map.route import ConcreteRouteSerializer, POIRouteSerializer
from utils.double_gis.service import DoubleGisService


class AbstractRouteView(views.APIView):
    permission_classes = (AllowAny,)
    api = DoubleGisService().get_api()

    def points_to_query(self, points):
        str_points = ['{} {}'.format(*point['coordinates']) for point in points]
        return ','.join(str_points)

    def serialize_linestring(self, linestring):
        result = [
            {
                'longitude': position[0],
                'latitude': position[1]
            } for position in linestring['coordinates']
            ]
        return result

    def build_route(self, points, alternative=0):
        query_points = self.points_to_query(points)
        response = self.api.transport.calculate_directions(
            waypoints=query_points,
            edge_filter='pedestrian',
            alternative=alternative,
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


class POIRouteView(AbstractRouteView):
    POINTS_COUNT = 8
    SPEED = 3 * 1000 / 60
    SEARCH_STRING = None
    serializer_class = POIRouteSerializer

    def estimate_walking_time(self, point1, point2):
        # Время в минутах
        return great_circle(point1['coordinates'], point2['coordinates']).meters / self.SPEED

    def get_search_polygon(self, start_point):
        coordinates = start_point['coordinates']
        point1 = Point((coordinates[0] - 0.029, coordinates[1] + 0.019))
        point2 = Point((coordinates[0] + 0.029, coordinates[1] - 0.019))
        return point1, point2

    def get_search_query_by_type(self, type):
        if type == POIRouteSerializer.BAR:
            return 'Бар'
        elif type == POIRouteSerializer.CULTURE:
            return 'Театр'
        elif type == POIRouteSerializer.FOOD:
            return 'Продукты'
        elif type == POIRouteSerializer.ROMANTIC:
            return 'Кинотеатр'
        elif type == POIRouteSerializer.INVESTIGATE:
            return 'Памятник'

    def search_organization(self, point1, point2, query):
        params = dict(
            point1='{},{}'.format(*point1['coordinates']),
            point2='{},{}'.format(*point2['coordinates']),
            fields='items.point',
            type='attraction,building,poi'
        )
        if query is not None:
            params['q'] = query
        response = self.api.catalog.branch.search(**params)
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        raw_point = response['result']['items'][0]['point']
        return Point((raw_point['lon'], raw_point['lat']))

    def search_geo_point(self, point1, point2, query):
        params = dict(
            point1='{},{}'.format(*point1['coordinates']),
            point2='{},{}'.format(*point2['coordinates']),
            fields='items.geometry.selection',
            type='attraction,building,poi'
        )
        if query is not None:
            params['q'] = query
        response = self.api.geo.search(**params)
        if response['meta']['code'] == 200:
            return wkt.loads(response['result']['items'][0]['geometry']['selection'])
        elif query is None:
            raise ValidationError(response)

    def search_destination(self, start_point, type):
        point1, point2 = self.get_search_polygon(start_point)
        query = self.get_search_query_by_type(type)
        result_point = self.search_geo_point(point1, point2, query)
        if result_point is None:
            return self.search_organization(point1, point2, query)
        return result_point

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_point = serializer.data['point']
        start_point = Point((raw_point['longitude'], raw_point['latitude']))
        end_point = self.search_destination(start_point, serializer.data['type'])
        print(
            'Оценочное время прогулки {walking_time} минут.'
                .format(walking_time=round(self.estimate_walking_time(start_point, end_point), 2))
        )
        return Response(
            self.serialize_linestring(self.build_route((start_point, end_point, start_point)))
        )


class ConcreteRouteView(AbstractRouteView):
    serializer_class = ConcreteRouteSerializer
    ALTERNATIVES_COUNT = 5

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_start_point = serializer.data['start_point']
        raw_end_point = serializer.data['end_point']
        start_point = Point((raw_start_point['longitude'], raw_start_point['latitude']))
        end_point = Point((raw_end_point['longitude'], raw_end_point['latitude']))
        return Response(
            self.serialize_linestring(
                self.build_route((start_point, end_point), self.ALTERNATIVES_COUNT)
            )
        )
