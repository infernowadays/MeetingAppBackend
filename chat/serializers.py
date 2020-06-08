from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, StringRelatedField
from .models import Message, PrivateMessage
from token_auth.serializers import UserProfileSerializer
from events.serializers import EventSerializer


class MessageSerializer(ModelSerializer):
    from_user = UserProfileSerializer(read_only=True)
    chat = serializers.IntegerField(source='event.id', read_only=True)

    # chat = EventSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, obj):
        message = super(MessageSerializer, self).to_representation(obj)
        message.pop('event')

        return message


class PrivateMessageSerializer(ModelSerializer):
    from_user = UserProfileSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = PrivateMessage
        fields = '__all__'
