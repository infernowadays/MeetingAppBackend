from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from common.models import Category
from .enums import Sex
import datetime
import os


def get_path_for_profile_photo(filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(datetime.datetime.now(), ext)
    return os.path.join(filename)


class ProfilePhoto(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    photo = models.FileField(upload_to=get_path_for_profile_photo)

    class Meta:
        db_table = 'profile_photo'


class UserProfileManager(BaseUserManager):
    def create_user(self, email, username, firebase_uid, password=None):
        if not email:
            raise ValueError("set email")
        if not username:
            raise ValueError("set username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            firebase_uid=firebase_uid
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            firebase_uid=firebase_uid,
            password=password
        )

        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=60)
    photo = models.ForeignKey(ProfilePhoto, null=True, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=10, choices=Sex.choices(), default=Sex.UNSURE.value)
    categories = models.ManyToManyField(Category, related_name='profiles', blank=True)
    firebase_uid = models.TextField(blank=True, null=False, max_length=128)
    firebase_registration_token = models.TextField(blank=True, max_length=256)
    # vk_token = models.TextField(null=True, max_length=128)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = UserProfileManager()

    class Meta:
        db_table = 'user_profile'
