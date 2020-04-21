from django.db import models
from token_auth.models import UserProfile
from .enums import Decision
from common.models import Category


class GeoPoint(models.Model):
    address = models.TextField(null=False)
    longitude = models.FloatField(null=False, default=0.0)
    latitude = models.FloatField(null=False, default=0.0)


class Event(models.Model):
    description = models.TextField(null=False, max_length=255)
    date = models.DateField(null=False)
    time = models.TimeField(null=True)
    ended = models.BooleanField(default=False)
    geo_point = models.ForeignKey(GeoPoint, null=False, on_delete=models.CASCADE)
    creator = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(UserProfile, related_name='events')
    categories = models.ManyToManyField(Category, related_name='events', blank=True)


class Request(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                related_name='to_user')
    from_user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                  related_name='from_user')
    created = models.DateTimeField(auto_now=True)
    seen = models.BooleanField(default=False)
    decision = models.CharField(
        max_length=10,
        choices=Decision.choices(),
        default=Decision.DECLINE.value
    )
