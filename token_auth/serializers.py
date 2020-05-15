from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer

from common.models import SubCategory
from common.serializers import SubCategorySerializer
from .models import UserProfile, ProfilePhoto, UserProfileCategories


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
    categories = SubCategorySerializer(many=True, read_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ["categories"]

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

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories')

        UserProfileCategories.objects.filter(user_profile=instance.id).delete()
        for string_category in categories:
            category = SubCategory.objects.filter(name=string_category.get('name'))
            if not category:
                category = SubCategory.objects.create(name=string_category.get('name'), parent_category_id='4')
            else:
                category = category.get()
            UserProfileCategories.objects.create(user_profile=instance, category=category)

        instance.save()
        return instance
