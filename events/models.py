from django.db import models

from common.models import Category, SubCategory
from token_auth.models import UserProfile
from .enums import Decision


class GeoPoint(models.Model):
    address = models.TextField(null=False)
    longitude = models.FloatField(null=False, default=0.0)
    latitude = models.FloatField(null=False, default=0.0)

    class Meta:
        db_table = 'geo_point'


class Event(models.Model):
    description = models.TextField(null=False, max_length=255)
    date = models.DateField(null=False)
    time = models.TimeField(null=True)
    ended = models.BooleanField(default=False)
    geo_point = models.ForeignKey(GeoPoint, null=False, on_delete=models.CASCADE)
    creator = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                related_name='creator_events')
    created = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(UserProfile, related_name='members_events')
    categories = models.ManyToManyField(SubCategory, through='EventCategories')

    class Meta:
        db_table = 'event'


class EventCategories(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = 'event_categories'
        unique_together = ['event', 'category']


class Request(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                related_name='to_user_requests')
    from_user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                  related_name='from_user_requests')
    created = models.DateTimeField(auto_now=True)
    seen = models.BooleanField(default=False)
    decision = models.CharField(
        max_length=16,
        choices=Decision.choices(),
        default=Decision.NO_ANSWER.value
    )

    class Meta:
        db_table = 'request'
        unique_together = ['event', 'to_user', 'from_user']
