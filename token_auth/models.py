from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from common.models import SubCategory
from .enums import Sex
import datetime
import os


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
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("set email")
        if not username:
            raise ValueError("set username")

        user = self.model(
            email=self.normalize_email(email),
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )

        user.set_password(password)

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=64, null=False)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

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
