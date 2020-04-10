from django.contrib.auth.models import User
from django.db import models
from token_auth.models import UserProfile


class Ticket(models.Model):
    name = models.TextField(null=False)
    price = models.FloatField(null=False)
    creator = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(null=True)
    description = models.TextField(null=True)
    sold = models.BooleanField(default=False)
