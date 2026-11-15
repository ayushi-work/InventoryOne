from django.urls import path

from . import views

urlpatterns = [
    path('api/auth/request-otp/', views.request_otp, name='request_otp'),
    path('api/auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/me/', views.me, name='me'),
    path('api/projects/', views.project_list, name='project_list'),
    path('api/projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('api/customers/', views.customers, name='customers'),
    path('api/bookings/', views.bookings, name='bookings'),
    path('api/commissions/', views.commissions, name='commissions'),
    path('api/admin/stats/', views.admin_stats, name='admin_stats'),
    path('api/admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('api/admin/bookings/<int:pk>/decide/', views.admin_decide_booking, name='admin_decide_booking'),
    path('api/admin/commissions/', views.admin_commissions, name='admin_commissions'),
    path('api/admin/commissions/<int:pk>/release/', views.admin_release_commission, name='admin_release_commission'),
]
