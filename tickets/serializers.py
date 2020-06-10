from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from common.serializers import SubCategorySerializer
from common.utils import set_geo_point, set_ticket_categories
from events.models import GeoPoint
from events.serializers import GeoPointSerializer
from token_auth.serializers import UserProfileSerializer
from .models import Ticket


class TicketSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    creator = UserProfileSerializer(read_only=True)
    categories = SubCategorySerializer(many=True, read_only=True, required=False)
    geo_point = GeoPointSerializer()

    class Meta:
        model = Ticket
        fields = '__all__'

    def create(self, validated_data):
        geo_point_validated = validated_data.pop('geo_point')
        geo_point = GeoPoint.objects.create(**geo_point_validated)
        ticket = Ticket.objects.create(geo_point=geo_point, **validated_data)

        categories = validated_data.pop('categories')
        if categories is not None:
            set_ticket_categories(categories, instance)

        return ticket

    def update(self, instance, validated_data):
        # instance.description = validated_data.pop('description')
        instance.price = validated_data.get('price', instance.price)
        instance.name = validated_data.get('name', instance.name)
        instance.date = validated_data.pop('date')
        instance.time = validated_data.get('time', instance.time)
        instance.save()

        categories = validated_data.pop('categories')
        if categories is not None:
            set_ticket_categories(categories, instance)

        set_geo_point(instance.geo_point, validated_data)

        return instance
