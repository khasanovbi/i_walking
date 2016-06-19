from geojson import Point
from geomet import wkt
from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import SearchSerializer
from utils.double_gis.service import DoubleGisService


class AbstractSearchView(views.APIView):
    permission_classes = (AllowAny,)
    api = DoubleGisService().get_api()
    serializer_class = SearchSerializer

    def get_region(self, point):
        response = self.api.region.search(q='{},{}'.format(*point['coordinates']))
        if response['meta']['code'] != 200:
            raise ValidationError(response)
        return response['result']['items'][0]['id']


class SearchByNameView(AbstractSearchView):
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


class SearchView(AbstractSearchView):
    def normalize_geo_response(self, raw_items):
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

    def normalize_branch_response(self, raw_items):
        result = []
        for raw_item in raw_items:
            raw_point = raw_item['point']
            if raw_point is not None:
                point_coordinates = raw_point['lon'], raw_point['lat']
                raw_item['geometry'] = {
                    'longitude': point_coordinates[0],
                    'latitude': point_coordinates[1]
                }
                for key in ('id', 'point', 'ads'):
                    del raw_item[key]
                result.append(raw_item)
        return result

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_point = serializer.data['point']
        start_point = Point((raw_point['longitude'], raw_point['latitude']))
        region_id = self.get_region(start_point)
        response = self.api.geo.search(
            q=serializer.data['query'],
            type='attraction,building,poi',
            fields='items.geometry.selection',
            region_id=region_id
        )
        if response['meta']['code'] != 200:
            response = self.api.catalog.branch.search(
                q=serializer.data['query'],
                region_id=region_id,
                fields='items.point'
            )
            raw_items = response['result']['items']
            items = self.normalize_branch_response(raw_items)
            if response['meta']['code'] != 200:
                raise ValidationError(response)
        else:
            raw_items = response['result']['items']
            items = self.normalize_geo_response(raw_items)
        return Response(items)
