from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


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
