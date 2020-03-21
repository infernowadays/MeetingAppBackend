from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Event, Invitation


class EventSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    creator_id = serializers.PrimaryKeyRelatedField(source='creator', read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'name', 'creator_id', 'created', 'description')


class InvitationSerializer(ModelSerializer):
    class Meta:
        model = Invitation
        fields = ('event', 'member', 'decision')
        extra_kwargs = {'decision': {'required': False}}
