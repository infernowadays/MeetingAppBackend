from django.contrib.auth.models import User
from django.db import models

from .enums import Decision


class GeoPoint(models.Model):
    longitude = models.DecimalField(null=False, max_digits=20, decimal_places=20)
    latitude = models.DecimalField(null=False, max_digits=20, decimal_places=20)


class Category(models.Model):
    name = models.TextField(null=False)


class Event(models.Model):
    name = models.TextField(null=False)
    creator = models.ForeignKey(User, null=False, db_constraint=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    address = models.TextField(null=False, default='')
    geo_point = models.ForeignKey(GeoPoint, null=True, on_delete=models.SET_NULL)
    description = models.TextField(null=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    members = models.ManyToManyField(User, related_name='events', through='Membership')
    categories = models.ManyToManyField(Category, related_name='events', through='Categorization')


class Categorization(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('event', 'category',)


class Membership(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('event', 'member',)


class Invitation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    decision = models.CharField(
        max_length=10,
        choices=Decision.choices(),
        default=Decision.DECLINE.value
    )

    class Meta:
        unique_together = ('event', 'member',)
