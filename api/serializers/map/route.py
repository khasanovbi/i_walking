from rest_framework import serializers


# noinspection PyAbstractClass
class InputRouteSerializer(serializers.Serializer):
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()


class SearchSerializer(InputRouteSerializer):
    query = serializers.CharField()
