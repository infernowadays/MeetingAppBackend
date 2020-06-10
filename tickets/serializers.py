from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from common.serializers import CategorySerializer
from events.serializers import GeoPointSerializer
from token_auth.serializers import UserProfileSerializer
from .models import Ticket


class TicketSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    creator = UserProfileSerializer(read_only=True)
    categories = CategorySerializer(read_only=True, many=True)
    geo_point = GeoPointSerializer()

    class Meta:
        model = Ticket
        fields = '__all__'

    def create(self, validated_data):
        geo_point_validated = validated_data.pop('geo_point')
        geo_point = GeoPoint.objects.create(**geo_point_validated)

        ticket = Ticket.objects.create(geo_point=geo_point, **validated_data)

        return ticket

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
