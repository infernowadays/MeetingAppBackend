from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from common.serializers import SubCategorySerializer
from common.utils import set_event_categories, set_geo_point
from token_auth.serializers import UserProfileSerializer
from .models import Event, Request, GeoPoint


class GeoPointSerializer(ModelSerializer):
    class Meta:
        model = GeoPoint
        fields = ('address', 'longitude', 'latitude')


class EventSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    creator = UserProfileSerializer(read_only=True)
    categories = SubCategorySerializer(many=True, read_only=True, required=False)
    members = UserProfileSerializer(read_only=True, many=True)
    geo_point = GeoPointSerializer()

    class Meta:
        model = Event
        fields = '__all__'

    def create(self, validated_data):
        geo_point_validated = validated_data.pop('geo_point')
        geo_point = GeoPoint.objects.create(**geo_point_validated)
        categories = validated_data.pop('categories')

        event = Event.objects.create(geo_point=geo_point, **validated_data)

        if categories is not None:
            set_event_categories(categories, event)

        return event

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.date = validated_data.get('date', instance.date)
        instance.time = validated_data.get('time', instance.time)
        instance.ended = validated_data.get('ended', instance.ended)
        instance.save()

        if validated_data.get('categories'):
            set_event_categories(validated_data.get('categories'), instance)

        if validated_data.get('geo_point'):
            set_geo_point(instance.geo_point, validated_data)

        return instance


class RequestSerializer(ModelSerializer):
    to_user = UserProfileSerializer(read_only=True)
    event = serializers.IntegerField(source='event.id', read_only=True)
    from_user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Request
        fields = '__all__'
        extra_kwargs = {'decision': {'required': False}}
