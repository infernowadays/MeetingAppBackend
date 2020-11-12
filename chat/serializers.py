from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from token_auth.serializers import UserProfileSerializer
from .models import Message, PrivateMessage, LastSeenMessage


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
    ticket = serializers.IntegerField(source='ticket.id', read_only=True)

    class Meta:
        model = PrivateMessage
        fields = '__all__'


class LastSeenMessageSerializer(ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    message = MessageSerializer(read_only=True)

    def create(self, validated_data):
        db_row = LastSeenMessage.objects.filter(chat_id=validated_data.get('chat_id'), user=validated_data.get('user'))
        if db_row:
            db_row.update(message_id=validated_data.get('message_id'))
            last_seen_message = db_row[0]
        else:
            last_seen_message = LastSeenMessage.objects.create(**validated_data)

        return last_seen_message

    class Meta:
        model = LastSeenMessage
        fields = '__all__'


class ChatSerializer(serializers.Serializer):
    content_type = serializers.CharField()
    content_id = serializers.IntegerField()
    title = serializers.CharField()
    from_user = UserProfileSerializer(read_only=True)
    last_message = serializers.CharField()
    last_message_id = serializers.IntegerField()
    last_seen_message_id = serializers.IntegerField()
    last_message_created = serializers.CharField()
    last_message_from_user_name = serializers.CharField()
