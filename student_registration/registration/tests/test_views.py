import pytest
from django.urls import reverse
from django.test import Client
from registration.models import Student
from registration.forms import StudentRegistrationForm

# Test 1: Test Student Model
@pytest.mark.django_db
def test_student_model():
    """
    Test the creation and string representation of the Student model.
    """
    student = Student.objects.create(
        name='John Doe',
        email='john@example.com',
        course='Python Programming',
        payment_status=False,
    )
    assert student.name == 'John Doe'
    assert student.email == 'john@example.com'
    assert student.course == 'Python Programming'
    assert student.payment_status is False
    assert str(student) == 'John Doe'  # Test __str__ method

# Test 2: Test Student Registration Form
@pytest.mark.django_db
def test_student_registration_form():
    """
    Test the StudentRegistrationForm with valid and invalid data.
    """
    # Test valid data
    valid_data = {
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'course': 'Django Development',
    }
    form = StudentRegistrationForm(data=valid_data)
    assert form.is_valid()

    # Test invalid data
    invalid_data = {
        'name': '',  # Name is required
        'email': 'invalid-email',  # Invalid email format
        'course': '',  # Course is required
    }
    form = StudentRegistrationForm(data=invalid_data)
    assert not form.is_valid()
    assert 'name' in form.errors
    assert 'email' in form.errors
    assert 'course' in form.errors

# Test 3: Test Registration View
@pytest.mark.django_db
def test_registration_view():
    """
    Test the register_student view for creating a new student and redirecting to the payment page.
    """
    client = Client()
    url = reverse('register')
    response = client.post(url, {
        'name': 'Alice',
        'email': 'alice@example.com',
        'course': 'Web Development',
    })
    assert response.status_code == 302  # Check for redirect
    assert Student.objects.filter(name='Alice').exists()

# Test 4: Test Payment View
@pytest.mark.django_db
def test_payment_view():
    """
    Test the payment view to ensure it renders the payment page correctly.
    """
    student = Student.objects.create(
        name='Bob',
        email='bob@example.com',
        course='Data Science',
        payment_status=False,
    )
    client = Client()
    url = reverse('payment', args=[student.id])
    response = client.get(url)
    assert response.status_code == 200
    assert 'student' in response.context
    assert response.context['student'].name == 'Bob'

# Test 5: Test Payment Success View
@pytest.mark.django_db
def test_payment_success_view():
    """
    Test the payment_success view to ensure it updates the payment_status to True.
    """
    student = Student.objects.create(
        name='Charlie',
        email='charlie@example.com',
        course='Machine Learning',
        payment_status=False,
    )
    client = Client()
    url = reverse('payment_success', args=[student.id])
    response = client.get(url)
    assert response.status_code == 200
    student.refresh_from_db()
    assert student.payment_status is True
