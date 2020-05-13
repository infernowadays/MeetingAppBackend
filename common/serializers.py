from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Category, SubCategory


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(ModelSerializer):
    parent_category = CategorySerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = '__all__'
