from django.test import TestCase

from events.models import Event, GeoPoint
from token_auth.models import UserProfile
from .models import PrivateMessage, Message


class ChatTestCase(TestCase):
    def setUp(self):
        from_user = UserProfile.objects.create(
            email='from_user@mail.ru',
            first_name='from_user_first_name',
            last_name='from_user_last_name',
            password='password'
        )
        UserProfile.objects.create(
            email='user@mail.ru',
            first_name='user_first_name',
            last_name='user_last_name',
            password='password'
        )
        Event.objects.create(
            description='event lalala',
            date='2020-05-31',
            creator=from_user,
            geo_point=GeoPoint.objects.create(
                address='address',
                longitude=0.0,
                latitude=0.0
            )
        )

    def test_private_massage_created(self):
        from_user = UserProfile.objects.get(email='from_user@mail.ru')
        user = UserProfile.objects.get(email='user@mail.ru')
        private_massage = PrivateMessage.objects.create(from_user=from_user, user=user, text='lalala')
        self.assertEqual(private_massage.text, 'lalala')

    def test_chat_massage_created(self):
        from_user = UserProfile.objects.get(email='from_user@mail.ru')
        event = Event.objects.get(creator=from_user)

        message = Message.objects.create(from_user=from_user, event=event, text='lalala chat')
        self.assertEqual(message.text, 'lalala chat')
