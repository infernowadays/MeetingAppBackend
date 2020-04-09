from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer

from .models import UserProfile, ProfilePhoto


class UserSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def to_representation(self, obj):
        user = super(UserSerializer, self).to_representation(obj)
        user.pop('password')
        return user

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.set_password(validated_data['password'])
            user.save()
        except KeyError:
            pass
        return user


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token
        fields = ['key']


class ProfilePhotoSerializer(ModelSerializer):
    class Meta:
        model = ProfilePhoto
        fields = '__all__'


class UserProfileSerializer(ModelSerializer):
    user = UserSerializer()
    photo = ProfilePhotoSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def to_representation(self, obj):
        profile = super(UserProfileSerializer, self).to_representation(obj)
        profile.pop('firebase_token')
        profile.pop('vk_token')

        return profile

    def create(self, validated_data):
        user_validated = validated_data.pop('user')
        user = User.objects.create_user(**user_validated)

        key_validated = validated_data.get('firebase_token')
        Token.objects.create(key=key_validated, user=user)

        profile = UserProfile.objects.create(user=user, **validated_data)

        return profile
