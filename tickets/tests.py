from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class TestTicketListView(APITestCase):
    def test_get_list(self):
        url = '/tickets/'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
