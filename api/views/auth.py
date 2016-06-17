from django.contrib.auth import authenticate, get_user_model, login
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import list_route
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, DjangoObjectPermissions
from rest_framework.response import Response

from api.serializers import SignInSerializer, SignUpSerializer, UserSerializer

User = get_user_model()


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    querysets = {
        'DEFAULT': User.objects.all(),
        'retrieve': User.objects.prefetch_related('members__band'),
    }
    permission_classes = (DjangoObjectPermissions,)
    queryset = User.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,)
    filter_fields = ('members__band',)
    search_fields = ('id', 'username', 'first_name', 'last_name')
    serializers = {
        'DEFAULT': UserSerializer,
        'sign_up': SignUpSerializer,
        'sign_in': SignInSerializer,
    }

    def get_queryset(self):
        return self.querysets.get(self.action, self.querysets['DEFAULT'])

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['DEFAULT'])

    @list_route(methods=['post'], permission_classes=(AllowAny,),
                parser_classes=(MultiPartParser,))
    def sign_up(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def sign_in(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.data)
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        else:
            return Response(
                {'error': 'Wrong username or password'},
                status=status.HTTP_403_FORBIDDEN
            )
