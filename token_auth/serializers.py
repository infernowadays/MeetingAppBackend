from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer
from firebase_admin import auth

from .models import UserProfile, ProfilePhoto
from common.serializers import CategorySerializer


class TokenSerializer(ModelSerializer):
    user = UserProfile

    class Meta:
        model = Token
        fields = ['key', 'user', ]


class ProfilePhotoSerializer(ModelSerializer):
    class Meta:
        model = ProfilePhoto
        fields = '__all__'


class UserProfileSerializer(ModelSerializer):
    photo = ProfilePhotoSerializer(read_only=True)
    categories = CategorySerializer(read_only=True, many=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def to_representation(self, obj):
        profile = super(UserProfileSerializer, self).to_representation(obj)
        profile.pop('password')
        profile.pop('is_active')
        profile.pop('is_admin')
        profile.pop('last_login')
        profile.pop('vk_token')

        return profile

    def create(self, validated_data):
        profile = UserProfile.objects.create_user(**validated_data)
        return profile
