import datetime
import os

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.contrib.auth.models import User
from django.db import models

from common.models import SubCategory
from .enums import Sex


def get_path_for_profile_photo(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(datetime.datetime.now(), ext)
    return os.path.join(filename)


class ProfilePhoto(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    photo = models.FileField(upload_to=get_path_for_profile_photo)

    class Meta:
        db_table = 'profile_photo'


class UserProfileManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("set email")
        if not first_name or not last_name:
            raise ValueError("provide first name and last name")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    first_name = models.CharField(max_length=64, null=False, blank=False)
    last_name = models.CharField(max_length=64, null=False, blank=False)
    city = models.CharField(max_length=64, null=True, blank=True)
    education = models.CharField(max_length=64, null=True, blank=True)
    job = models.CharField(max_length=64, null=True, blank=True)
    photo = models.ForeignKey(ProfilePhoto, null=True, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=16, choices=Sex.choices(), default=Sex.UNSURE.value)
    categories = models.ManyToManyField(SubCategory, through='UserProfileCategories')
    firebase_uid = models.TextField(blank=True, max_length=128)
    vk_token = models.TextField(null=True, blank=True, max_length=128)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_filled = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    objects = UserProfileManager()

    class Meta:
        db_table = 'user_profile'


class UserProfileCategories(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = 'user_profile_categories'
        unique_together = ['user_profile', 'category']


class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    class Meta:
        db_table = 'users_groups'
