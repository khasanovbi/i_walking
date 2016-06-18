from rest_framework import serializers


# noinspection PyAbstractClass
class PointSerializer(serializers.Serializer):
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()


# noinspection PyAbstractClass
class SearchSerializer(PointSerializer):
    query = serializers.CharField()


# noinspection PyAbstractClass
class ConcreteRouteSerializer(serializers.Serializer):
    start_point = PointSerializer()
    end_point = PointSerializer()
