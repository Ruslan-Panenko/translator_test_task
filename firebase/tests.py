from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch


class TranslationsListAPIViewTest(APITestCase):

    @patch('firebase.views.verify', return_value={'email': 'test@example.com'})
    def test_get_list_of_translations(self, mock_verify):
        """
        Test to verify the GET request for list of translations returns HTTP_200_OK status code
        """
        url = reverse('translations_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('firebase.views.verify', return_value=None)
    def test_get_list_of_translations_with_invalid_token(self, mock_verify):
        """
        Test to verify the GET request for list of translations with an invalid token returns HTTP_403_FORBIDDEN status code
        """
        url = reverse('translations_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('firebase.views.verify', return_value=None)
    @patch('firebase.views.db.collection')
    def test_post_new_translation(self, mock_collection, mock_verify):
        """
        Test to verify the POST request for new translation returns HTTP_201_CREATED status code
        """
        url = reverse('translations_list')
        data = {'input_text': 'hello', 'output_text': 'hola'}
        with patch.object(mock_collection(u'translations').document(), 'set', return_value=None) as mock_set:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertFalse(mock_set.called)

    @patch('firebase.views.verify', return_value=None)
    def test_post_new_translation_with_invalid_token(self, mock_verify):
        """
        Test to verify the POST request for new translation with an invalid token returns HTTP_403_FORBIDDEN status code
        """
        url = reverse('translations_list')
        data = {'input_text': 'hello', 'output_text': 'hola'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
