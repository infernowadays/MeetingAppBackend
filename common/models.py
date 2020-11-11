from django.db import models


class Category(models.Model):
    name = models.TextField(null=False, unique=True)

    class Meta:
        db_table = 'category'


class SubCategory(models.Model):
    name = models.TextField(null=False, unique=True)
    parent_category = models.ForeignKey(Category, null=False, on_delete=models.CASCADE, related_name='sub_categories')

    class Meta:
        db_table = 'sub_category'


class Feedback(models.Model):
    text = models.TextField(null=False)
    user = models.IntegerField(null=False, blank=True)

    class Meta:
        db_table = 'feedback'
