from django.test import TestCase

from token_auth.models import UserProfile
from .models import Event, GeoPoint


class EventTestCase(TestCase):
    def setUp(self):
        geo_point = GeoPoint.objects.create(
            address='address',
            longitude=0.0,
            latitude=0.0
        )
        creator = UserProfile.objects.create(
            email='email@mail.ru',
            first_name='first_name',
            last_name='last_name',
            password='password'
        )
        Event.objects.create(
            description='for remove',
            date='2020-05-31',
            creator=creator,
            geo_point=geo_point
        )

    def test_event_creation(self):
        creator = UserProfile.objects.get(email='email@mail.ru')
        geo_point = GeoPoint.objects.get(address='address')

        event = Event.objects.create(
            description='to go for a walk',
            date='2020-05-31',
            creator=creator,
            geo_point=geo_point
        )

        self.assertEqual(event.description, 'to go for a walk')

    def test_event_removed(self):
        self.assertTrue(Event.objects.filter(description='for remove').exists())

        event = Event.objects.get(description='for remove')
        event.delete()

        self.assertFalse(Event.objects.filter(description='for remove').exists())
