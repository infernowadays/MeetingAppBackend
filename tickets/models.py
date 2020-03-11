from django.contrib.auth.models import User
from django.db import models


class Ticket(models.Model):
    name = models.TextField(default='')
    price = models.FloatField(null=False)
    seller = models.ForeignKey(User, null=False, db_constraint=True, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    description = models.TextField(null=True)
    sold = models.BooleanField(default=False)
