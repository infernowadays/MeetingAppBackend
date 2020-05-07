from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, StringRelatedField
from .models import Chat, Message


class ChatSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'


class MessageSerializer(ModelSerializer):
    chat = ChatSerializer(read_only=True, many=True)

    class Meta:
        model = Message
        fields = '__all__'
