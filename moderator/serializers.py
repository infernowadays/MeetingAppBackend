from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from token_auth.serializers import UserProfileSerializer
from .models import Complaint, UserProfileWarning


class ComplaintSerializer(ModelSerializer):
    suspected = UserProfileSerializer(read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'


class UserProfileWarningSerializer(ModelSerializer):
    user_profile = serializers.IntegerField(source='user_profile.id', read_only=True)
    complaint = serializers.IntegerField(source='complaint.id', read_only=True)

    class Meta:
        model = UserProfileWarning
        fields = '__all__'
