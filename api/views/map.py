from geojson import LineString, Point
from geomet import wkt
from geopy.distance import great_circle
from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers.map.route import (
    ConcreteRouteSerializer, POIRouteSerializer, SearchSerializer
)
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

    def search_destination(self, start_point, type):
        point1, point2 = self.get_search_polygon(start_point)
        params = dict(
            point1='{},{}'.format(*point1['coordinates']),
            point2='{},{}'.format(*point2['coordinates']),
            fields='items.geometry.selection'
        )
        query = self.get_search_query_by_type(type)
        if query is not None:
            params['q'] = query

        response = self.api.geo.search(**params)
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        return wkt.loads(response['result']['items'][0]['geometry']['selection'])

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


class SearchByNameView(views.APIView):
    api = DoubleGisService().get_api()
    serializer_class = SearchSerializer

    def get_region(self, point):
        response = self.api.region.search(q='{},{}'.format(*point['coordinates']))
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        return response['result']['items'][0]['id']

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_point = Point((serializer.data['longitude'], serializer.data['latitude']))
        region_id = self.get_region(start_point)
        response = self.api.catalog.branch.search(
            q=serializer.data['query'],
            region_id=region_id
        )
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        return Response(response['result']['items'])


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


class SearchView(views.APIView):
    api = DoubleGisService().get_api()
    serializer_class = SearchSerializer

    def get_region(self, point):
        response = self.api.region.search(q='{},{}'.format(*point['coordinates']))
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        return response['result']['items'][0]['id']

    def normalize_response(self, raw_items):
        result = []
        for raw_item in raw_items:
            raw_point = raw_item['geometry']['selection']
            point_coordinates = wkt.loads(raw_point)['coordinates']
            raw_item['geometry'] = {
                'longitude': point_coordinates[0],
                'latitude': point_coordinates[1]
            }
            result.append(raw_item)
        return result

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_point = Point((serializer.data['longitude'], serializer.data['latitude']))
        region_id = self.get_region(start_point)
        response = self.api.geo.search(
            q=serializer.data['query'],
            type='attraction,building,poi',
            fields='items.geometry.selection',
            region_id=region_id
        )
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        raw_items = response['result']['items']
        items = self.normalize_response(raw_items)
        return Response(items)
