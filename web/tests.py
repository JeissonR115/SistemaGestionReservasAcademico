from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class HomePageTests(TestCase):
    def test_anonymous_user_sees_login_form(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar sesión')
        self.assertContains(response, 'login-form')

    def test_requester_sees_reservation_controls(self):
        user = User.objects.create_user(
            username='web-requester',
            password='RequesterPass123!',
        )
        self.client.force_login(user)

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Solicitar un espacio')
        self.assertContains(response, 'data-role="requester"')

    def test_administrator_sees_space_and_review_controls(self):
        admin = User.objects.create_user(
            username='web-admin',
            password='AdminPass123!',
            role=User.Role.ADMINISTRATOR,
        )
        self.client.force_login(admin)

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crear espacio')
        self.assertContains(response, 'Solicitudes pendientes')

# Create your tests here.
