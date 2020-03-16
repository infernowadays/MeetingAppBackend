from django.contrib.auth.models import User
from django.db import models

from .enums import Decision


class GeoPoint(models.Model):
    longitude = models.DecimalField(null=False, max_digits=20, decimal_places=20)
    latitude = models.DecimalField(null=False, max_digits=20, decimal_places=20)


class Category(models.Model):
    name = models.TextField(null=False, unique=True)


class Event(models.Model):
    name = models.TextField(null=False)
    creator = models.ForeignKey(User, null=False, db_constraint=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    address = models.TextField(null=False, default='')
    geo_point = models.ForeignKey(GeoPoint, null=True, on_delete=models.SET_NULL)
    description = models.TextField(null=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    members = models.ManyToManyField(User, related_name='events')
    categories = models.ManyToManyField(Category, related_name='events')


class Invitation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    decision = models.CharField(
        max_length=10,
        choices=Decision.choices(),
        default=Decision.DECLINE.value
    )
