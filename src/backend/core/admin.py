from django.contrib import admin

from .models import (
    AuditLog,
    Booking,
    Broker,
    Commission,
    CompanyProfile,
    Customer,
    Document,
    Notification,
    OTPCode,
    Plot,
    Project,
    SupportTicket,
)


@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'kyc_status', 'rera_number', 'agreement_accepted')
    list_filter = ('kyc_status',)
    search_fields = ('user__email', 'user__first_name', 'pan_number', 'rera_number')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'code', 'location')


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('project', 'plot_number', 'size_sq_yds', 'facing', 'status', 'total_cost')
    list_filter = ('status', 'project')
    search_fields = ('plot_number',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'broker', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'plot', 'broker', 'token_amount', 'status', 'created_at')
    list_filter = ('status', 'payment_mode')
    search_fields = ('customer__name', 'plot__plot_number')


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('booking', 'broker', 'amount', 'tds_amount', 'net_amount', 'released')
    list_filter = ('released',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'broker', 'size_bytes', 'created_at')
    list_filter = ('kind',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'broker', 'kind', 'read', 'created_at')
    list_filter = ('kind', 'read')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'broker', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'actor_name', 'entity_type', 'entity_id')
    list_filter = ('action', 'entity_type')
    search_fields = ('action', 'actor_name', 'entity_id')


admin.site.register(OTPCode)
admin.site.register(CompanyProfile)
