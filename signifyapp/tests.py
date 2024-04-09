from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from .models import Component, Invoice # Załóżmy, że nazwa twojej aplikacji to 'myapp'

class UserAuthenticationTestCase(TestCase):
    def setUp_user(self):
        # Tworzenie użytkownika testowego
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client = Client()

    def setUp_admin(self):
        # Tworzenie użytkownika testowego
        self.username = 'admin'
        self.password = 'adminpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client = Client()

    def test_user_login(self):
        # Sprawdź, czy użytkownik może się zalogować z poprawnymi danymi
        login_successful = self.client.login(username='testuser', password='testpassword')
        self.assertTrue(login_successful)
        
        # Sprawdź, czy użytkownik jest teraz zalogowany
        user = User.objects.get(username=self.username)
        self.assertTrue(user.is_authenticated)

    def test_admin_login(self):
        # Sprawdź, czy użytkownik może się zalogować z poprawnymi danymi
        login_successful = self.client.login(username='admin', password='adminpassword')
        self.assertTrue(login_successful)
        
        # Sprawdź, czy użytkownik jest teraz zalogowany
        user = User.objects.get(username=self.username)
        self.assertTrue(user.is_authenticated)
    
    def test_user_logout(self):       
        # Wyloguj użytkownika
        self.client.logout()

    def deleteAccountUser(self):
        # Utwórz użytkownika do testów
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.get(username=self.username, password=self.password)
        self.user.delete()

    def deleteAccountAdmin(self):
        # Utwórz użytkownika do testów
        self.username = 'admin'
        self.password = 'adminpassword'
        self.user = User.objects.get(username=self.username, password=self.password)
        self.user.delete()

class ComponentTestCase(TestCase):
    def setUpFalse(self):
        # Tworzenie użytkownika testowego
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Tworzenie rekordów komponentów dla użytkownika testowego
        Component.objects.create(user=self.user, average=5)

    def setUpTrue(self):
        # Tworzenie użytkownika testowego
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Tworzenie rekordów komponentów dla użytkownika testowego
        Component.objects.create(user=self.user, average=15)

    def tearDown(self):
        # Usunięcie danych testowych
        User.objects.filter(username='testuser').delete()

class InvoiceModelTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(username='test_user', password='password123')

    def test_invoice_creation(self):
        # Tworzenie nowej faktury z ręcznie ustawioną datą płatności
        invoice = Invoice.objects.create(
            payment_due_date='2024-04-06',
            user=self.user,
            is_paid=False
        )

        # Sprawdzenie, czy faktura została utworzona pomyślnie
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.user, self.user)
        self.assertFalse(invoice.is_paid)

    def test_invoice_deletion(self):
        # Tworzenie nowej faktury
        invoice = Invoice.objects.create(
            payment_due_date='2024-04-06',
            user=self.user,
            is_paid=False
        )

        # Usuwanie faktury
        invoice.delete()

        # Spróbowanie odzyskać usuniętą fakturę
        try:
            deleted_invoice = Invoice.objects.get(pk=invoice.pk)
        except Invoice.DoesNotExist:
            deleted_invoice = None

        # Sprawdzenie, czy faktura została pomyślnie usunięta
        self.assertIsNone(deleted_invoice)

    def test_invoice_update(self):
        # Tworzenie nowej faktury
        invoice = Invoice.objects.create(
            payment_due_date='2024-04-06',
            user=self.user,
            is_paid=False
        )

        # Aktualizacja faktury
        invoice.is_paid = True
        invoice.save()

        # Pobranie zaktualizowanej faktury z bazy danych
        updated_invoice = Invoice.objects.get(pk=invoice.pk)

        # Sprawdzenie, czy faktura została pomyślnie zaktualizowana
        self.assertTrue(updated_invoice.is_paid)

    def tearDown(self):
        # Clean up test data
        User.objects.all().delete()
        Invoice.objects.all().delete()

class InvoiceListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Tworzymy testowego użytkownika
        test_user = User.objects.create_user(username='testuser', password='testpassword')
        test_user.save()

        # Tworzymy kilka testowych faktur
        number_of_invoices = 5
        for invoice_id in range(number_of_invoices):
            Invoice.objects.create(user=test_user, number=f'INV00{invoice_id}', amount=(invoice_id + 1) * 100)

    def tearDown(self):
        # Czyszczenie danych testowych po każdym teście
        User.objects.filter(username='testuser').delete()

