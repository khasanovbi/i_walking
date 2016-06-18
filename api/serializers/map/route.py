from rest_framework import serializers


# noinspection PyAbstractClass
class PointSerializer(serializers.Serializer):
    longitude = serializers.FloatField(min_value=-90, max_value=90)
    latitude = serializers.FloatField(min_value=-180, max_value=180)


# noinspection PyAbstractClass
class POIRouteSerializer(serializers.Serializer):
    INVESTIGATE = 'investigate'
    ROMANTIC = 'romantic'
    RANDOM = 'random'
    FOOD = 'food'
    BAR = 'bar'
    CULTURE = 'culture'
    POI_CHOICES = (
        (INVESTIGATE, INVESTIGATE),
        (ROMANTIC, ROMANTIC),
        (RANDOM, RANDOM),
        (FOOD, FOOD),
        (BAR, BAR),
        (CULTURE, CULTURE),
    )
    type = serializers.ChoiceField(choices=POI_CHOICES)
    point = PointSerializer()


# noinspection PyAbstractClass
class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    point = PointSerializer()


# noinspection PyAbstractClass
class ConcreteRouteSerializer(serializers.Serializer):
    start_point = PointSerializer()
    end_point = PointSerializer()
