from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from token_auth.serializers import UserSerializer
from .models import Event, Invitation, Category


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class EventSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    creator = UserSerializer(read_only=True)
    categories = CategorySerializer(read_only=True, many=True)

    # creator_id = serializers.PrimaryKeyRelatedField(source='creator', read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'name', 'creator', 'created', 'address', 'description', 'categories')


class InvitationSerializer(ModelSerializer):
    class Meta:
        model = Invitation
        fields = ('event', 'member', 'decision')
        extra_kwargs = {'decision': {'required': False}}
