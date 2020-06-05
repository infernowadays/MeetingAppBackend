from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class TestTicketListView(APITestCase):
    def test_get_tickets(self):
        url = '/api/tickets/'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
