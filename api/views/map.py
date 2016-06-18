import requests
from django.conf import settings
from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class RouteView(views.APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        return Response(
            requests.get(
                'http://catalog.api.2gis.ru/2.0/region/list?key={key}'
                    .format(key=settings.DOUBLE_GIS_API_KEY)
            ).json()['result']
        )
