import unittest
from django.test import Client
from django.contrib.auth.models import User
from .models import Invoice, Light, Component
from django.utils import timezone
from django.urls import reverse

class TestViews(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(self.user)

    def test_login_existing_view(self):
        response = self.client.post(reverse('login_existing'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)  # should redirect to notifications

    def test_signup_view(self):
        response = self.client.post(reverse('signup'), {'username': 'newuser', 'password1': 'newpassword', 'password2': 'newpassword'})
        self.assertEqual(response.status_code, 302)  # should redirect to notifications

    def test_logout_view(self):
        response = self.client.get(reverse('logout_view'))
        self.assertEqual(response.status_code, 302)  # should redirect to login

    def test_check_payment_deadline_authenticated(self):
        invoice = Invoice.objects.create(user=self.user, payment_due_date=timezone.now().date())
        light = Light.objects.create(invoice=invoice)
        response = self.client.get(reverse('check_payment_deadline'))
        self.assertEqual(response.status_code, 200)  # should render template.html

    def test_display_records_with_average_above_10_authenticated(self):
        component = Component.objects.create(user=self.user, average=15)
        response = self.client.get(reverse('display_records_with_average_above_10'))
        self.assertEqual(response.status_code, 200)  # should render template_with_records.html

    def test_index_authenticated(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)  # should render index.html

    def test_index_start_stop(self):
        response_start = self.client.post(reverse('index'), {'start': True})
        self.assertEqual(response_start.status_code, 200)  # should render index.html
        response_stop = self.client.post(reverse('index'), {'stop': True})
        self.assertEqual(response_stop.status_code, 200)  # should render index.html

    def tearDown(self):
        self.client.logout()
        self.user.delete()

if __name__ == '__main__':
    unittest.main()