from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from token_auth.serializers import UserProfileSerializer
from .models import Event, Request, GeoPoint
from common.serializers import CategorySerializer
import datetime


class GeoPointSerializer(ModelSerializer):
    class Meta:
        model = GeoPoint
        fields = ('address', 'longitude', 'latitude')


class EventSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    creator = UserProfileSerializer(read_only=True)
    categories = CategorySerializer(read_only=True, many=True)
    geo_point = GeoPointSerializer()

    class Meta:
        model = Event
        fields = ('id', 'creator', 'created', 'description', 'categories', 'geo_point', 'date', 'time')

    def create(self, validated_data):
        geo_point_validated = validated_data.pop('geo_point')
        geo_point = GeoPoint.objects.create(**geo_point_validated)
        event = Event.objects.create(geo_point=geo_point, **validated_data)

        return event


class RequestSerializer(ModelSerializer):
    # from_user = UserProfileSerializer(read_only=True)
    # to_user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Request
        fields = '__all__'
        extra_kwargs = {'decision': {'required': False}}
