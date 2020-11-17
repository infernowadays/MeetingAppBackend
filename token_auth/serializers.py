from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer, Serializer

from common.serializers import SubCategorySerializer
from common.utils import set_user_profile_categories
from .models import UserProfile, ProfilePhoto


class DynamicFieldsModelSerializer(ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class TokenSerializer(ModelSerializer):
    user = UserProfile

    class Meta:
        model = Token
        fields = ['key', 'user', ]


class ProfilePhotoSerializer(ModelSerializer):
    class Meta:
        model = ProfilePhoto
        fields = '__all__'


class UserProfileSerializer(DynamicFieldsModelSerializer):
    photo = ProfilePhotoSerializer(read_only=True)
    categories = SubCategorySerializer(many=True, read_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ["categories"]

    def to_representation(self, obj):
        profile = super(UserProfileSerializer, self).to_representation(obj)
        if profile.get('password') is not None:
            profile.pop('password')
            profile.pop('is_active')
            profile.pop('is_admin')
            profile.pop('is_staff')
            profile.pop('is_superuser')
            profile.pop('last_login')
            profile.pop('user_permissions')
            profile.pop('groups')
        # profile.pop('vk_token')
        return profile

    def create(self, validated_data):
        profile = UserProfile.objects.create_user(**validated_data)
        return profile

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories')
        if categories is not None:
            set_user_profile_categories(categories, instance)

        instance.city = validated_data.get('city', instance.city)
        instance.job = validated_data.get('job', instance.job)
        instance.education = validated_data.get('education', instance.education)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.sex = validated_data.get('sex', instance.sex)
        instance.is_filled = validated_data.get('is_filled', instance.is_filled)
        instance.save()

        return instance


class AuthCredentialsSerializers(Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class ForgetPasswordSerializers(Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
