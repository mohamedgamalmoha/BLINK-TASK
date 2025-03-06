from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.enums import UserRole
from accounts.models import User
from accounts.factories import UserFactory
from accounts.api.permissions import IsOwner


class UserViewSetTestCase(APITestCase):

    def setUp(self):
        # Create users using the factory
        self.admin_user = UserFactory(
            username='admin',
            role=UserRole.ADMIN.value
        )

        self.customer_user = UserFactory(
            username='customer',
            role=UserRole.LOAN_CUSTOMER.value
        )

        self.client = APIClient()

    def test_create_user_no_auth_required(self):
        """
        Test that anyone can create a user without authentication
        """
        url = reverse('accounts:users-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': UserRole.LOAN_CUSTOMER.value
        }

        # Make request without authentication
        response = self.client.post(url, data, format='json')

        # Assert user creation is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)
        self.assertEqual(User.objects.get(username='newuser').email, 'newuser@example.com')

    def test_list_users_permission_denied(self):
        """
        Test that unauthenticated users cannot list users
        """
        url = reverse('accounts:users-list')
        response = self.client.get(url)

        # Assert permission denied without authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_user_allowed(self):
        """
        Test that a user can retrieve their own user details
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('accounts:users-detail', kwargs={'pk': self.customer_user.id})

        response = self.client.get(url)

        # Assert user can access their own details
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')

    def test_retrieve_other_user_denied(self):
        """
        Test that a user cannot retrieve other user details
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('accounts:users-detail', kwargs={'pk': self.admin_user.id})

        response = self.client.get(url)

        # Assert user cannot access other user's details
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_own_user_allowed(self):
        """
        Test that a user can update their own user details
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('accounts:users-detail', kwargs={'pk': self.customer_user.id})

        data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }

        response = self.client.patch(url, data, format='json')

        # Assert user can update their own details
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.email, 'updated@example.com')
        self.assertEqual(self.customer_user.first_name, 'Updated')

    def test_update_other_user_denied(self):
        """
        Test that a user cannot update other user details
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('accounts:users-detail', kwargs={'pk': self.admin_user.id})

        data = {
            'email': 'hacked@example.com'
        }

        response = self.client.patch(url, data, format='json')

        # Assert user cannot update other user's details
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.admin_user.refresh_from_db()
        self.assertNotEqual(self.admin_user.email, 'hacked@example.com')

    def test_delete_own_user_allowed(self):
        """
        Test that a user can delete their own account
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('accounts:users-detail', kwargs={'pk': self.customer_user.id})

        response = self.client.delete(url)

        # Assert user can delete their own account
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.filter(id=self.customer_user.id).count(), 0)

    def test_delete_other_user_denied(self):
        """
        Test that a user cannot delete other users
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('accounts:users-detail', kwargs={'pk': self.admin_user.id})

        response = self.client.delete(url)

        # Assert user cannot delete other users
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.filter(id=self.admin_user.id).count(), 1)

    def test_serializer_excludes_sensitive_fields(self):
        """
        Test that the serializer excludes sensitive fields
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('accounts:users-detail', kwargs={'pk': self.customer_user.id})

        response = self.client.get(url)

        # Assert password and other sensitive fields are not included
        self.assertNotIn('password', response.data)
        self.assertNotIn('is_superuser', response.data)
        self.assertNotIn('is_staff', response.data)
        self.assertNotIn('groups', response.data)
        self.assertNotIn('user_permissions', response.data)

    def test_create_multiple_users_with_factory(self):
        """
        Test creating multiple users with different roles using the factory
        """
        # Create 5 random users with different roles
        users = [UserFactory() for _ in range(5)]

        # Verify all users were created with expected attributes
        self.assertEqual(User.objects.count(), 7)  # 5 new + 2 from setup

        # Check that each user has the expected fields from the factory
        for user in users:
            self.assertIsNotNone(user.username)
            self.assertTrue(user.username.startswith('user_'))
            self.assertEqual(user.email, f'{user.username}@example.com')
            self.assertIsNotNone(user.first_name)
            self.assertIsNotNone(user.last_name)
            self.assertTrue(user.is_active)
            self.assertTrue(user.check_password('defaultpassword'))
            # Role should be one of the valid roles except ADMIN (as defined in factory)
            self.assertIn(user.role, [role.value for role in UserRole if role != UserRole.ADMIN])


class IsOwnerPermissionTest(TestCase):

    def setUp(self):
        self.customer_user = UserFactory(
            username='customer',
            role=UserRole.LOAN_CUSTOMER.value
        )

        self.other_user = UserFactory(
            username='other',
            role=UserRole.LOAN_CUSTOMER.value
        )

        # Import the IsOwner permission class
        self.permission = IsOwner()

    def test_is_owner_permission(self):
        """
        Test the IsOwner permission logic
        """

        # Mock a request object with a user
        class MockRequest:
            def __init__(self, user):
                self.user = user

        # Create mock objects
        request = MockRequest(self.customer_user)
        view = None

        # Test when object is the user themselves
        self.assertTrue(self.permission.has_object_permission(request, view, self.customer_user))

        # Test when object is a different user
        self.assertFalse(self.permission.has_object_permission(request, view, self.other_user))

    def test_bulk_user_creation_with_factory(self):
        """
        Test the factory can create multiple users with unique attributes
        """
        initial_count = User.objects.count()

        # Create 10 users in bulk
        users = UserFactory.create_batch(10)

        # Verify all users were created
        self.assertEqual(User.objects.count(), initial_count + 10)

        # Verify each user has unique username
        usernames = [user.username for user in users]
        self.assertEqual(len(usernames), len(set(usernames)), "Usernames should be unique")

        # Verify all required fields are populated
        for user in users:
            self.assertIsNotNone(user.email)
            self.assertIsNotNone(user.first_name)
            self.assertIsNotNone(user.last_name)
            self.assertTrue(user.is_active)
            # Verify password was set correctly
            self.assertTrue(user.check_password('defaultpassword'))
