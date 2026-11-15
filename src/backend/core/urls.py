from django.urls import path

from . import views

urlpatterns = [
    # --- health probe ---------------------------------------------------
    path('api/health/', views.health, name='health'),

    # --- authentication -------------------------------------------------
    path('api/auth/request-otp/', views.request_otp, name='request_otp'),
    path('api/auth/verify-otp/', views.verify_otp, name='verify_otp'),

    # --- broker ---------------------------------------------------------
    path('api/me/', views.me, name='me'),
    path('api/kyc/summary/', views.kyc_summary, name='kyc_summary'),

    # --- projects & inventory -------------------------------------------
    path('api/projects/', views.project_list, name='project_list'),
    path('api/projects/<int:pk>/', views.project_detail, name='project_detail'),

    # --- customers & bookings -------------------------------------------
    path('api/customers/', views.customers, name='customers'),
    path('api/bookings/', views.bookings, name='bookings'),

    # --- earnings --------------------------------------------------------
    path('api/commissions/', views.commissions, name='commissions'),

    # --- notifications ---------------------------------------------------
    path('api/notifications/', views.notification_list, name='notification_list'),
    path('api/notifications/unread-count/', views.notification_unread_count,
         name='notification_unread_count'),
    path('api/notifications/mark-read/', views.notification_mark_read,
         name='notification_mark_read'),

    # --- support ---------------------------------------------------------
    path('api/tickets/', views.tickets, name='tickets'),
    path('api/company/', views.company_profile, name='company_profile'),

    # --- documents -------------------------------------------------------
    path('api/documents/', views.document_list, name='document_list'),
    path('api/documents/<int:pk>/', views.document_delete, name='document_delete'),
    path('api/documents/<int:pk>/download/', views.document_download, name='document_download'),
    path('api/projects/<int:pk>/price-list/', views.generate_price_list,
         name='generate_price_list'),
    path('api/bookings/<int:pk>/demand-letter/', views.generate_demand_letter,
         name='generate_demand_letter'),

    # --- administration ---------------------------------------------------
    path('api/admin/stats/', views.admin_stats, name='admin_stats'),
    path('api/admin/projects/', views.admin_projects, name='admin_projects'),
    path('api/admin/projects/<int:pk>/', views.admin_project_update, name='admin_project_update'),
    path('api/admin/projects/<int:pk>/plots/', views.admin_plots, name='admin_plots'),
    path('api/admin/plots/<int:pk>/', views.admin_plot_update, name='admin_plot_update'),
    path('api/admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('api/admin/bookings/<int:pk>/decide/', views.admin_decide_booking,
         name='admin_decide_booking'),
    path('api/admin/commissions/', views.admin_commissions, name='admin_commissions'),
    path('api/admin/commissions/<int:pk>/release/', views.admin_release_commission,
         name='admin_release_commission'),
    path('api/admin/tickets/', views.admin_tickets, name='admin_tickets'),
    path('api/admin/brokers/', views.admin_brokers, name='admin_brokers'),
    path('api/admin/broadcast/', views.admin_broadcast, name='admin_broadcast'),
    path('api/admin/audit-log/', views.admin_audit_log, name='admin_audit_log'),
]
