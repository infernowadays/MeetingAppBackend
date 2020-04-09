from django.contrib.auth.models import User
from django.db import models

from events.models import Category
from .enums import Sex
import datetime
import os


def path_and_rename(filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(datetime.datetime.now(), ext)
    return os.path.join(filename)


def get_path_for_my_model_file(instance, filename):
    return path_and_rename(filename)


class ProfilePhoto(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    photo = models.FileField(upload_to=get_path_for_my_model_file)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=False)
    photo = models.ForeignKey(ProfilePhoto, null=True, on_delete=models.CASCADE)
    birth = models.DateField(null=False)
    sex = models.CharField(max_length=10, choices=Sex.choices(), default=Sex.UNSURE.value)
    categories = models.ManyToManyField(Category, related_name='profiles', blank=True)
    firebase_uid = models.TextField(null=False, max_length=128)
    firebase_token = models.TextField(null=False, max_length=255)
    vk_token = models.TextField(null=True, max_length=128)
