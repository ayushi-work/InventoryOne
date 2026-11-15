from django.urls import path

from . import views

urlpatterns = [
    path('api/auth/request-otp/', views.request_otp, name='request_otp'),
    path('api/auth/verify-otp/', views.verify_otp, name='verify_otp'),
]
