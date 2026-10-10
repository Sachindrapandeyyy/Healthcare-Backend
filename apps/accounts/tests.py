from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User

class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.valid_user_data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'SecurePassword123'
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertEqual(response.data['user']['name'], 'Test User')
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())

    def test_register_user_duplicate_email(self):
        self.client.post(self.register_url, self.valid_user_data, format='json')
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success', True))

    def test_register_user_missing_fields(self):
        response = self.client.post(self.register_url, {'email': 'incomplete@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success(self):
        self.client.post(self.register_url, self.valid_user_data, format='json')
        login_data = {
            'email': 'testuser@example.com',
            'password': 'SecurePassword123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')

    def test_login_user_invalid_credentials(self):
        self.client.post(self.register_url, self.valid_user_data, format='json')
        login_data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success', True))

    def test_login_user_not_found(self):
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'Password123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_blacklists_token_success(self):
        self.client.post(self.register_url, self.valid_user_data, format='json')
        login_resp = self.client.post(
            self.login_url,
            {'email': 'testuser@example.com', 'password': 'SecurePassword123'},
            format='json'
        )
        access_token = login_resp.data['access']
        refresh_token = login_resp.data['refresh']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_resp = self.client.post(
            self.logout_url,
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)
        self.assertIn('blacklisted', logout_resp.data['message'].lower())
