from django.db import models

from token_auth.models import UserProfile
from .enums import ContentType


class Complaint(models.Model):
    user_profile = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                     related_name='complaints')
    content_id = models.IntegerField(null=False, blank=False)
    content_type = models.CharField(
        max_length=8,
        choices=ContentType.choices(),
        null=False,
        blank=False
    )
    reviewed = models.BooleanField(default=False)

    class Meta:
        db_table = 'complaint'


class UserProfileWarning(models.Model):
    user_profile = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                     related_name='warnings')

    class Meta:
        db_table = 'user_profile_warning'
