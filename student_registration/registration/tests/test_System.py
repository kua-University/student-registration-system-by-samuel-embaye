import pytest
from django.urls import reverse
from django.test import Client
from registration.models import Student
import stripe
from django.conf import settings

# Set up Stripe test keys
stripe.api_key = settings.STRIPE_SECRET_KEY

@pytest.mark.django_db
def test_student_registration():
    """
    Test that a student can register successfully.
    """
    client = Client()
    url = reverse('register')

    # Simulate a POST request with valid data
    response = client.post(url, {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'course': 'Python Programming',
    })

    # Check that the student was created
    assert Student.objects.count() == 1
    student = Student.objects.first()
    assert student.name == 'John Doe'
    assert student.email == 'john.doe@example.com'
    assert student.course == 'Python Programming'
    assert student.payment_status is False

    # Check that the user is redirected to the payment page
    assert response.status_code == 302
    assert response.url == reverse('payment', args=[student.id])

@pytest.mark.django_db
def test_payment_flow(mocker):
    """
    Test the payment flow, including Stripe Checkout redirection.
    """
    client = Client()

    # Create a student for testing
    student = Student.objects.create(
        name='Jane Doe',
        email='jane.doe@example.com',
        course='Django Development',
        payment_status=False,
    )

    # Mock Stripe Checkout Session creation
    mock_session = mocker.patch('registration.views.stripe.checkout.Session.create')
    mock_session.return_value = mocker.MagicMock(url='https://checkout.stripe.com/test_session')
    # Simulate a POST request to the payment view
    url = reverse('payment', args=[student.id])
    response = client.post(url)

    # Check that the user is redirected to Stripe Checkout
    assert response.status_code == 302
    assert response.url == 'https://checkout.stripe.com/test_session'

    # Verify that the Stripe Session was created with the correct parameters
    mock_session.assert_called_once_with(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Course: {student.course}',
                },
                'unit_amount': 5000,  # $50.00 in cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'http://127.0.0.1:8000/register/payment_success/{student.id}/',
        cancel_url=f'http://127.0.0.1:8000/register/payment_failed/{student.id}/',
        metadata={'student_id': student.id},
    )
@pytest.mark.django_db
def test_payment_success():
    """
    Test that the payment status is updated after a successful payment.
    """
    client = Client()

    # Create a student for testing
    student = Student.objects.create(
        name='Alice Smith',
        email='alice.smith@example.com',
        course='Data Science',
        payment_status=False,
    )

    # Simulate a GET request to the payment_success view
    url = reverse('payment_success', args=[student.id])
    response = client.get(url)

    # Check that the payment status is updated
    student.refresh_from_db()
    assert student.payment_status is True

    # Check that the success page is rendered
    assert response.status_code == 200
    assert b'Payment Successful!' in response.content

@pytest.mark.django_db
def test_payment_failed():
    """
    Test that the payment failed page is displayed correctly.
    """
    client = Client()

    # Create a student for testing
    student = Student.objects.create(
        name='Bob Johnson',
        email='bob.johnson@example.com',
        course='Web Development',
        payment_status=False,
    )

    # Simulate a GET request to the payment_failed view
    url = reverse('payment_failed', args=[student.id])
    response = client.get(url)

    # Check that the failed page is rendered
    assert response.status_code == 200
    assert b'Payment Failed' in response.content