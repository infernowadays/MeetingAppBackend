from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from common.serializers import SubCategorySerializer, SubCategory
from token_auth.serializers import UserProfileSerializer
from .models import Event, Request, GeoPoint, EventCategories


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
            EventCategories.objects.filter(event=event.id).delete()
            for string_category in categories:
                category = SubCategory.objects.filter(name=string_category.get('name'))
                category = category.get()
                EventCategories.objects.create(event=event, category=category)

        return event

    def update(self, instance, validated_data):
        instance.description = validated_data.pop('description')
        instance.date = validated_data.pop('date')
        instance.time = validated_data.get('time', instance.time)
        instance.save()

        categories = validated_data.pop('categories')
        if categories is not None:
            EventCategories.objects.filter(event=instance.id).delete()
            for string_category in categories:
                category = SubCategory.objects.filter(name=string_category.get('name'))
                if not category:
                    category = SubCategory.objects.create(name=string_category.get('name'), parent_category_id='4')
                else:
                    category = category.get()
                EventCategories.objects.create(event=instance, category=category)

        geo_point = instance.geo_point
        geo_point.latitude = validated_data.get('geo_point').get('latitude')
        geo_point.longitude = validated_data.get('geo_point').get('longitude')
        geo_point.address = validated_data.get('geo_point').get('address')
        geo_point.save()

        return instance


class RequestSerializer(ModelSerializer):
    to_user = serializers.IntegerField(source='to_user.id', read_only=True)
    event = serializers.IntegerField(source='event.id', read_only=True)
    from_user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Request
        fields = '__all__'
        extra_kwargs = {'decision': {'required': False}}

#####
class SendRequestSerializer(ModelSerializer):
    to_user = serializers.IntegerField(source='to_user.id', read_only=True)
    from_user = UserProfileSerializer(read_only=True)
    event = serializers.IntegerField(source='event.id', read_only=True)

    class Meta:
        model = Request
        fields = '__all__'
        extra_kwargs = {'decision': {'required': False}}


class GetRequestSerializer(ModelSerializer):
    to_user = UserProfileSerializer(read_only=True)
    from_user = UserProfileSerializer(read_only=True)
    event = serializers.IntegerField(source='event.id', read_only=True)

    class Meta:
        model = Request
        fields = '__all__'
