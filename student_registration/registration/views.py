from django.shortcuts import render, redirect
from .forms import StudentRegistrationForm
from .models import Student
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, 'registration/home.html')

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.payment_status = False  # Payment not completed yet
            student.save()
            return redirect('payment', student_id=student.id)
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def payment(request, student_id):
    student = Student.objects.get(id=student_id)
    if request.method == 'POST':
        try:
            # Create a Stripe Checkout Session
            session = stripe.checkout.Session.create(
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
            return redirect(session.url)  # Redirect to Stripe Checkout Page
        except stripe.error.StripeError as e:
            return render(request, 'registration/payment_failed.html')
    return render(request, 'registration/payment.html', {'student': student})

def payment_success(request, student_id):
    student = Student.objects.get(id=student_id)
    student.payment_status = True
    student.save()
    return render(request, 'registration/payment_success.html', {'student': student})

def payment_failed(request, student_id):
    student = Student.objects.get(id=student_id)
    return render(request, 'registration/payment_failed.html', {'student': student})