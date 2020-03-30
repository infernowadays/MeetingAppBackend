from django.contrib.auth.models import User
from django.db import models

from events.models import Category
from .enums import Sex


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=False)
    birth = models.DateField(null=False)
    sex = models.CharField(max_length=10, choices=Sex.choices(), default=Sex.UNSURE.value)
    categories = models.ManyToManyField(Category, related_name='profiles', blank=True)
    firebase_uid = models.TextField(null=False, max_length=128)
    firebase_token = models.TextField(null=False, max_length=255)
    vk_token = models.TextField(null=True, max_length=128)
