from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APITestCase

User = get_user_model()


class AccountApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='AdminPass123!',
            role=User.Role.ADMINISTRATOR,
        )
        self.requester = User.objects.create_user(
            username='requester',
            password='RequesterPass123!',
        )

    def test_active_user_signs_in(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'requester',
            'password': 'RequesterPass123!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['role'], User.Role.REQUESTER)
        self.assertIn('sessionid', self.client.cookies)

    def test_inactive_user_sign_in_is_rejected(self):
        self.requester.is_active = False
        self.requester.save(update_fields=('is_active',))

        response = self.client.post('/api/auth/login/', {
            'username': 'requester',
            'password': 'RequesterPass123!',
        })

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('sessionid', self.client.cookies)

    def test_authenticated_user_signs_out(self):
        self.client.post('/api/auth/login/', {
            'username': 'requester',
            'password': 'RequesterPass123!',
        })

        response = self.client.post('/api/auth/logout/')

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get('/api/users/').status_code, 403)

    def test_login_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        token_response = client.get('/api/auth/csrf/')
        self.assertEqual(token_response.status_code, 200)

        response = client.post('/api/auth/login/', {
            'username': 'requester',
            'password': 'RequesterPass123!',
        })
        self.assertEqual(response.status_code, 403)

        response = client.post(
            '/api/auth/login/',
            {
                'username': 'requester',
                'password': 'RequesterPass123!',
            },
            HTTP_X_CSRFTOKEN=token_response.data['csrfToken'],
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_creates_and_deactivates_user_account(self):
        self.client.force_authenticate(user=self.admin)
        created = self.client.post('/api/users/', {
            'username': 'new-user',
            'email': 'new@example.com',
            'role': User.Role.REQUESTER,
            'password': 'NewPass123!',
        })

        self.assertEqual(created.status_code, 201)
        user = User.objects.get(username='new-user')
        self.assertTrue(user.check_password('NewPass123!'))
        self.assertNotIn('password', created.data)

        updated = self.client.patch(
            f'/api/users/{user.pk}/',
            {'is_active': False},
        )

        self.assertEqual(updated.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_admin_can_assign_valid_role(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f'/api/users/{self.requester.pk}/',
            {'role': User.Role.ADMINISTRATOR},
        )

        self.assertEqual(response.status_code, 200)
        self.requester.refresh_from_db()
        self.assertEqual(self.requester.role, User.Role.ADMINISTRATOR)

    def test_superuser_is_created_with_administrator_role(self):
        superuser = User.objects.create_superuser(
            username='root',
            email='root@example.com',
            password='RootPass123!',
        )

        self.assertEqual(superuser.role, User.Role.ADMINISTRATOR)

    def test_account_without_valid_role_is_rejected(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post('/api/users/', {
            'username': 'invalid-role',
            'password': 'ValidPass123!',
            'role': 'root',
        })

        self.assertEqual(response.status_code, 400)

    def test_requester_cannot_perform_administrative_actions(self):
        self.client.force_authenticate(user=self.requester)

        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_perform_protected_operations(self):
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, 403)

# Create your tests here.
