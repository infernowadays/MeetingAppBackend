from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import ModelSerializer

from events.models import Event
# from token_auth.serializers import UserSerializer


class TicketSerializer(ModelSerializer):
    creator_id = serializers.PrimaryKeyRelatedField(source='creator', read_only=True)

    class Meta:
        model = Event
        fields = ('name', 'creator_id', 'created', 'description')
