from django.db import models

from events.models import Event
from tickets.models import Ticket
from token_auth.models import UserProfile


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

    # ticket = models.ForeignKey(Ticket, null=False, db_constraint=True, on_delete=models.CASCADE,
    #                            related_name='messages')

    class Meta:
        db_table = 'private_message'


class LastSeenMessage(models.Model):
    chat_id = models.IntegerField(null=False, blank=False)
    message_id = models.IntegerField(null=False, blank=False)
    user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                             related_name='last_messages')

    class Meta:
        db_table = 'last_seen_message'
