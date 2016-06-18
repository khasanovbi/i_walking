from rest_framework import serializers


# noinspection PyAbstractClass
class InputRouteSerializer(serializers.Serializer):
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()
    time = serializers.IntegerField()
