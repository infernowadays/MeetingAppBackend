from django.contrib.auth.models import User
from django.db import models

from common.models import Category
from common.models import SubCategory
from events.models import GeoPoint
from token_auth.models import UserProfile


class Ticket(models.Model):
    name = models.TextField(null=False)
    price = models.FloatField(null=False)
    geo_point = models.ForeignKey(GeoPoint, null=False, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    row = models.IntegerField(null=True, blank=True)
    zone = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)
    sold = models.BooleanField(default=False)
    categories = models.ManyToManyField(SubCategory, through='TicketCategories')

    class Meta:
        db_table = 'ticket'


class TicketCategories(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = 'ticket_categories'
        unique_together = ['ticket', 'category']
