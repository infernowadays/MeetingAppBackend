from django.db import models


class Category(models.Model):
    name = models.TextField(null=False, unique=True)

    class Meta:
        db_table = 'category'


class SubCategory(models.Model):
    name = models.TextField(null=False, unique=True)
    parent_category = models.ForeignKey(Category, null=False, blank=True, on_delete=models.CASCADE,
                                        related_name='sub_categories')

    class Meta:
        db_table = 'sub_category'
