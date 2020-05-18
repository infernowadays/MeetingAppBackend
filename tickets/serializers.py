from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from common.serializers import CategorySerializer
from token_auth.serializers import UserProfileSerializer
from .models import Ticket


class TicketSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    creator = UserProfileSerializer(read_only=True)
    categories = CategorySerializer(read_only=True, many=True)

    class Meta:
        model = Ticket
        fields = '__all__'
