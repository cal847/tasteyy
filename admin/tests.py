from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()
class UserAPITests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='AdminPass123'
        )
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='UserPass123'
        )
        self.client = APIClient()
    
    def test_user_list_requires_admin(self):
        """
        Ensure that only admin users can list all users.
        """
        url = reverse('user-list')  # from router.register('users', ...)
        
        # Attempt as regular user
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Attempt as admin user
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2)

    def test_admin_promote_and_demote_user(self):
        """
        Ensure admin can promote and demote users via AdminUserViewSet.
        """
        promote_url = reverse('admin-users-promote', args=[self.regular_user.pk])
        demote_url = reverse('admin-users-demote', args=[self.regular_user.pk])

        # Must be authenticated as admin
        self.client.force_authenticate(user=self.admin_user)

        # Promote user
        promote_resp = self.client.post(promote_url)
        self.assertEqual(promote_resp.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_staff)
        self.assertTrue(self.regular_user.is_superuser)

        # Demote user
        demote_resp = self.client.post(demote_url)
        self.assertEqual(demote_resp.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_staff)
        self.assertFalse(self.regular_user.is_superuser)

    def test_admin_delete_user(self):
        """
        Ensure admin can delete a user.
        """
        delete_url = reverse('admin-users-detail', args=[self.regular_user.pk])
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.regular_user.pk)
        