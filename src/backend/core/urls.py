from django.urls import path

from . import views

urlpatterns = [
    path('api/auth/request-otp/', views.request_otp, name='request_otp'),
    path('api/auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/me/', views.me, name='me'),
    path('api/projects/', views.project_list, name='project_list'),
    path('api/projects/<int:pk>/', views.project_detail, name='project_detail'),
]
