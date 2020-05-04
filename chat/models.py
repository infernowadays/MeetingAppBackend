from django.db import models
from token_auth.models import UserProfile


class Chat(models.Model):
    members = models.ManyToManyField(UserProfile, related_name='chats')

    class Meta:
        db_table = 'chat'


class Message(models.Model):
    from_user = models.ForeignKey(UserProfile, null=False, db_constraint=True, on_delete=models.CASCADE,
                                  related_name='from_user_messages')
    text = models.TextField(null=False, max_length=512)
    created = models.DateTimeField(auto_now=True)
    seen = models.BooleanField(default=False)
    chat = models.ForeignKey(Chat, null=False, db_constraint=True, on_delete=models.CASCADE, related_name='messages')

    class Meta:
        db_table = 'message'
