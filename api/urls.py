from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from api.views import *
from api.views.auth import UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet)

route_urlpatterns = [
    url('^concrete', ConcreteRouteView.as_view()),
    url('^poi', POIRouteView.as_view()),
]

map_urlpatterns = [
    url('^route/', include(route_urlpatterns)),
    url('^search', SearchView.as_view()),
]

urlpatterns = [
    url('', include(router.urls)),
    url('^map/', include(map_urlpatterns))
]
