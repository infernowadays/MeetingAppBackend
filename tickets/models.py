from django.contrib.auth.models import User
from django.db import models

from common.models import Category
from events.models import GeoPoint
from token_auth.models import UserProfile


class Ticket(models.Model):
    name = models.TextField(null=False)
    price = models.FloatField(null=False)
    row = models.IntegerField(null=True, blank=True)
    place = models.IntegerField(null=True, blank=True)
    zone = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(null=True)
    description = models.TextField(null=True, blank=True)
    sold = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name='tickets', blank=True)

    class Meta:
        db_table = 'ticket'
