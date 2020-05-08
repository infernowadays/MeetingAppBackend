from django.db import models

from token_auth.models import UserProfile
from events.models import Event


class Message(models.Model):
    from_user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                  related_name='from_user_messages')
    text = models.TextField(null=False, max_length=512)
    created = models.DateTimeField(auto_now=True)
    seen = models.BooleanField(default=False)
    event = models.ForeignKey(Event, null=False, db_constraint=True, on_delete=models.CASCADE, related_name='messages')

    class Meta:
        db_table = 'message'


class PrivateMessage(models.Model):
    from_user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                  related_name='private_from_user_messages')
    user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                             related_name='private_user_messages')
    text = models.TextField(null=False, max_length=512)
    created = models.DateTimeField(auto_now=True)
    seen = models.BooleanField(default=False)

    class Meta:
        db_table = 'private_message'
