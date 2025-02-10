from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_student, name='register'),
    path('payment/<int:student_id>/', views.payment, name='payment'),
    path('payment_success/<int:student_id>/', views.payment_success, name='payment_success'),
    path('payment_failed/<int:student_id>/', views.payment_failed, name='payment_failed'),
]