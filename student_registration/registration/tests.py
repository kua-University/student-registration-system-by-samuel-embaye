from django.test import TestCase, Client
from django.urls import reverse
from registration.models import Student
from registration.forms import StudentRegistrationForm
import stripe
from unittest.mock import patch, Mock

class RegistrationIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'course': 'Python Programming',
        }

    def test_registration_flow(self):
        """
        Test the student registration flow:
        1. Submit the registration form.
        2. Verify the student is saved to the database.
        3. Verify the user is redirected to the payment page.
        """
        # Simulate a POST request to the registration view
        response = self.client.post(self.register_url, self.form_data)

        # Check that the student is created in the database
        student = Student.objects.get(email='john@example.com')
        self.assertEqual(student.name, 'John Doe')
        self.assertEqual(student.course, 'Python Programming')
        self.assertFalse(student.payment_status)

        # Check that the user is redirected to the payment page
        self.assertRedirects(response, reverse('payment', args=[student.id]))

    def test_registration_form_validation(self):
        """
        Test the registration form validation:
        1. Submit invalid data (missing name).
        2. Verify the form is not valid.
        3. Verify the user is not redirected.
        """
        invalid_data = {
            'name': '',  # Missing name
            'email': 'john@example.com',
            'course': 'Python Programming',
        }
        response = self.client.post(self.register_url, invalid_data)

        # Check that the form is not valid
        form = response.context['form']
        self.assertFalse(form.is_valid())

        # Check that the user is not redirected
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')


class PaymentIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            course='Django Development',
            payment_status=False,
        )
        self.payment_url = reverse('payment', args=[self.student.id])

    @patch('stripe.checkout.Session.create')
    def test_payment_flow(self, mock_stripe_session):
        """
        Test the payment flow:
        1. Mock Stripe's API to simulate a successful payment.
        2. Verify the user is redirected to Stripe's checkout page.
        3. Simulate a successful payment callback.
        4. Verify the payment status is updated in the database.
        5. Verify the payment success page is rendered.
        """
        # Create a mock object with a 'url' attribute
        mock_session = Mock()
        mock_session.url = 'https://stripe.com/checkout'
        mock_stripe_session.return_value = mock_session

        # Simulate a POST request to the payment view
        response = self.client.post(self.payment_url)

        # Check that the user is redirected to Stripe's checkout page
        self.assertEqual(response.status_code, 302)
        self.assertIn('https://stripe.com/checkout', response.url)

        # Simulate a successful payment callback
        success_url = reverse('payment_success', args=[self.student.id])
        response = self.client.get(success_url)

        # Check that the payment status is updated in the database
        self.student.refresh_from_db()
        self.assertTrue(self.student.payment_status)

        # Check that the payment success page is rendered
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/payment_success.html')


class PaymentFailureIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            name='Alice',
            email='alice@example.com',
            course='Web Development',
            payment_status=False,
        )
        self.payment_url = reverse('payment', args=[self.student.id])

    @patch('stripe.checkout.Session.create')
    def test_payment_failure_flow(self, mock_stripe_session):
        """
        Test the payment failure flow:
        1. Mock Stripe's API to simulate a payment failure.
        2. Verify the user is redirected to the payment failure page.
        3. Verify the payment status remains unchanged.
        """
        # Mock Stripe's error
        mock_stripe_session.side_effect = stripe.error.StripeError("Payment failed")

        # Simulate a POST request to the payment view
        response = self.client.post(self.payment_url)

        # Check that the user is redirected to the payment failure page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/payment_failed.html')

        # Check that the payment status remains unchanged
        self.student.refresh_from_db()
        self.assertFalse(self.student.payment_status)