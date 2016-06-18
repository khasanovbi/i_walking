from urllib.parse import urlencode, urlparse, urlunparse

import requests
from django.conf import settings


class DoubleGisMethod:
    def __init__(self, api, method=None):
        self.api = api
        self._method = method

    def __getattr__(self, method):
        if self._method:
            self._method += '/' + method
            return self

        return DoubleGisMethod(self.api, method)

    def __call__(self, **kwargs):
        return self.api.method(self._method, kwargs)


class DoubleGisService(object):
    BASE_URL = 'http://catalog.api.2gis.ru/2.0/'

    def __init__(self, key=None):
        if not key:
            self.key = settings.DOUBLE_GIS_API_KEY

    def get_api(self):
        return DoubleGisMethod(self)

    def method(self, method, params):
        url_parts = list(urlparse(self.BASE_URL))
        url_parts[2] += method
        params['key'] = self.key
        url_parts[4] = urlencode(params)
        url = urlunparse(url_parts)
        print(url)
        return requests.get(url).json()
