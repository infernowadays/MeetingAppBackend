from django.db import models


class Category(models.Model):
    name = models.TextField(null=False, unique=True)
