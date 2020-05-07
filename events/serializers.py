from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, StringRelatedField

from token_auth.serializers import UserProfileSerializer
from .models import Event, Request, GeoPoint
from chat.models import Chat
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
    members = UserProfileSerializer(read_only=True, many=True)
    geo_point = GeoPointSerializer()

    class Meta:
        model = Event
        fields = ('id', 'creator', 'created', 'description', 'categories', 'members', 'geo_point', 'date', 'time')

    def create(self, validated_data):
        geo_point_validated = validated_data.pop('geo_point')
        geo_point = GeoPoint.objects.create(**geo_point_validated)

        chat = Chat.objects.create()

        event = Event.objects.create(geo_point=geo_point, chat=chat, **validated_data)

        return event

    def update(self, instance, validated_data):
        instance.description = validated_data.pop('description')
        instance.date = validated_data.pop('date')
        instance.time = validated_data.get('time', instance.time)
        instance.save()

        geo_point = instance.geo_point
        geo_point.latitude = validated_data.get('geo_point').get('latitude')
        geo_point.longitude = validated_data.get('geo_point').get('longitude')
        geo_point.address = validated_data.get('geo_point').get('address')
        geo_point.save()

        return instance


class RequestSerializer(ModelSerializer):
    from_user = StringRelatedField(read_only=True)
    to_user = StringRelatedField(read_only=True)
    event = serializers.IntegerField(source='event.id', read_only=True)

    class Meta:
        model = Request
        fields = '__all__'
        extra_kwargs = {'decision': {'required': False}}
