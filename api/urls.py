from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from api.views import RouteView
from api.views.auth import UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet)

urlpatterns = [
    url('', include(router.urls)),
    url('^route', RouteView.as_view())
]
