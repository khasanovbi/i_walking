from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from api.views import RandomRouteView
from api.views.auth import UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet)

route_urlpatterns = [
    url('^random', RandomRouteView.as_view()),
    # url('^random', RouteView.as_view()),
    # url('^random', RouteView.as_view()),
    # url('^random', RouteView.as_view()),
]

map_urlpatterns = [
    url('^route/', include(route_urlpatterns))
]

urlpatterns = [
    url('', include(router.urls)),
    url('^map/', include(map_urlpatterns))
]
