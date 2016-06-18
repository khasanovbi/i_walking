from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from api.views import *
from api.views.auth import UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet)

route_urlpatterns = [
    url('^investigate', InvestigateRouteView.as_view()),
    url('^food', FoodRouteView.as_view()),
    url('^bar', BarRouteView.as_view()),
    url('^culture', CultureRouteView.as_view()),
    url('^romantic', RomanticRouteView.as_view()),
    url('^random', RandomRouteView.as_view()),
]

map_urlpatterns = [
    url('^route/', include(route_urlpatterns)),
    url('^search', SearchView.as_view()),
]

urlpatterns = [
    url('', include(router.urls)),
    url('^map/', include(map_urlpatterns))
]
