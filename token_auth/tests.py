from django.test import TestCase

from .models import UserProfile


class UserProfileTestCase(TestCase):
    def setUp(self):
        UserProfile.objects.create(
            email='email@mail.ru',
            first_name='first_name',
            last_name='last_name',
            password='password'
        )

    def test_user_profile_creation(self):
        user_profile = UserProfile.objects.get(email='email@mail.ru')
        self.assertEqual(user_profile.first_name, 'first_name')

    def test_user_profile_removed(self):
        self.assertTrue(UserProfile.objects.filter(email='email@mail.ru').exists())

        user_profile = UserProfile.objects.filter(email='email@mail.ru')
        user_profile.delete()

        self.assertFalse(UserProfile.objects.filter(email='email@mail.ru').exists())
