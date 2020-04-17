from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer
from firebase_admin import auth

from .models import UserProfile, ProfilePhoto


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
    # user = UserSerializer()
    photo = ProfilePhotoSerializer(required=False)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def to_representation(self, obj):
        profile = super(UserProfileSerializer, self).to_representation(obj)
        profile.pop('password')
        # profile.pop('firebase_token')
        profile.pop('is_active')
        profile.pop('is_admin')
        profile.pop('last_login')

        # profile.pop('vk_token')

        return profile

    def create(self, validated_data):
        # user_validated = validated_data.pop('user')
        # user = User.objects.create_user(**user_validated)
        #
        # key_validated = validated_data.get('firebase_token')
        # Token.objects.create(key=key_validated, user_=user)

        profile = UserProfile.objects.create_user(**validated_data)

        # key_validated = validated_data.get('firebase_token')
        # Token.objects.create(key=key_validated, user=profile)

        return profile


def create_firebase_account(email, password):
    auth.create_user(email=email, password=password)
