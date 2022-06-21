from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class GetBasicTest(APITestCase):
    def __init__(self, url):
        super().__init__()
        self._url = reverse(url)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = reverse(value)

    def test_accessibility(self):
        """Test if POST request is possible"""
        response = self.client.post(self._url)
        self.assertNotEqual(response, status.HTTP_404_NOT_FOUND)
