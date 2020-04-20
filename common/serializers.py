from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Category


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']
