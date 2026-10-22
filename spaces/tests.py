from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Space

User = get_user_model()


class SpaceApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='space-admin',
            password='AdminPass123!',
            role=User.Role.ADMINISTRATOR,
        )
        self.requester = User.objects.create_user(
            username='space-requester',
            password='RequesterPass123!',
        )
        self.active_space = Space.objects.create(
            name='Laboratorio A',
            space_type='Laboratorio',
            capacity=25,
        )
        self.inactive_space = Space.objects.create(
            name='Auditorio B',
            space_type='Auditorio',
            capacity=100,
            is_active=False,
        )

    def test_admin_creates_valid_space(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post('/api/spaces/', {
            'name': 'Sala de cómputo',
            'space_type': 'Sala de cómputo',
            'capacity': 30,
            'is_active': True,
        })

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Space.objects.filter(name='Sala de cómputo', capacity=30).exists()
        )

    def test_space_rejects_non_positive_capacity(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post('/api/spaces/', {
            'name': 'Espacio inválido',
            'space_type': 'Laboratorio',
            'capacity': 0,
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('capacity', response.data)

    def test_admin_updates_and_deactivates_space(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f'/api/spaces/{self.active_space.pk}/',
            {'capacity': 40},
        )
        self.assertEqual(response.status_code, 200)
        self.active_space.refresh_from_db()
        self.assertEqual(self.active_space.capacity, 40)

        response = self.client.delete(
            f'/api/spaces/{self.active_space.pk}/',
        )
        self.assertEqual(response.status_code, 204)
        self.active_space.refresh_from_db()
        self.assertFalse(self.active_space.is_active)

    def test_requester_sees_active_space_details(self):
        self.client.force_authenticate(user=self.requester)

        response = self.client.get('/api/spaces/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Laboratorio A')
        self.assertEqual(response.data[0]['capacity'], 25)

    def test_inactive_space_is_not_available_in_catalog(self):
        self.client.force_authenticate(user=self.requester)

        response = self.client.get('/api/spaces/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            self.inactive_space.pk,
            [item['id'] for item in response.data],
        )

    def test_requester_cannot_manage_spaces(self):
        self.client.force_authenticate(user=self.requester)

        response = self.client.post('/api/spaces/', {
            'name': 'No autorizado',
            'space_type': 'Laboratorio',
            'capacity': 10,
        })

        self.assertEqual(response.status_code, 403)

# Create your tests here.
