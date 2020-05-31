from django.db import models


class ConfirmationCode(models.Model):
    email = models.TextField(null=False, blank=False)
    code = models.IntegerField(null=False, blank=True)

    class Meta:
        db_table = 'confirmation_code'
