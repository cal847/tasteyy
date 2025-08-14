from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAPITests(APITestCase):
    def setUp(self):
        # Create user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='UserPass123'
        )
        self.client = APIClient()

    def test_register_user(self):
        """
        Ensure a user can register and receive JWT tokens.
        """
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewUserPass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_user(self):
        """
        Ensure a registered user can login and receive JWT tokens.
        """
        url = reverse('login')
        data = {
            'email': self.regular_user.email,
            'password': 'UserPass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_logout_user(self):
        """
        Ensure a logged-in user can logout by blacklisting the refresh token.
        """
        # Login first to get tokens
        login_url = reverse('login')
        login_data = {'email': self.regular_user.email, 'password': 'UserPass123'}
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        logout_url = reverse('logout')
        response = self.client.post(logout_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    