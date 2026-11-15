import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Broker(models.Model):
    KYC_PENDING = 'pending'
    KYC_APPROVED = 'approved'
    KYC_REJECTED = 'rejected'
    KYC_CHOICES = [
        (KYC_PENDING, 'Pending'),
        (KYC_APPROVED, 'Approved'),
        (KYC_REJECTED, 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='broker')
    phone = models.CharField(max_length=15, blank=True)
    kyc_status = models.CharField(max_length=10, choices=KYC_CHOICES, default=KYC_PENDING)
    pan_number = models.CharField(max_length=20, blank=True)
    aadhaar_number = models.CharField(max_length=20, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    rera_number = models.CharField(max_length=30, blank=True)
    bank_account = models.CharField(max_length=30, blank=True)
    ifsc = models.CharField(max_length=20, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class OTPCode(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    @property
    def is_valid(self):
        return self.expires_at > timezone.now()

    @classmethod
    def generate_for(cls, email):
        cls.objects.filter(email=email).delete()
        return cls.objects.create(
            email=email,
            code=f'{random.randint(0, 999999):06d}',
            expires_at=timezone.now() + timedelta(minutes=5),
        )


class Project(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_UPCOMING = 'upcoming'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_UPCOMING, 'Upcoming'),
        (STATUS_CLOSED, 'Closed'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Plot(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_ON_HOLD = 'on_hold'
    STATUS_SOLD = 'sold'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_ON_HOLD, 'On Hold'),
        (STATUS_SOLD, 'Sold'),
    ]

    FACINGS = [
        ('E', 'East'), ('W', 'West'), ('N', 'North'), ('S', 'South'),
        ('NE', 'North-East'), ('NW', 'North-West'), ('SE', 'South-East'), ('SW', 'South-West'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='plots')
    plot_number = models.CharField(max_length=20)
    size_sq_yds = models.DecimalField(max_digits=10, decimal_places=2)
    facing = models.CharField(max_length=5, choices=FACINGS)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default=STATUS_AVAILABLE, db_index=True)
    bsp = models.DecimalField(max_digits=10, decimal_places=2)  # per sq.yd
    plc_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        ordering = ['plot_number']
        constraints = [
            models.UniqueConstraint(fields=['project', 'plot_number'], name='uniq_plot_per_project'),
        ]

    @property
    def total_cost(self):
        base = self.size_sq_yds * self.bsp
        base *= 1 + (self.plc_pct or Decimal('0')) / Decimal('100')
        base *= 1 - (self.discount_pct or Decimal('0')) / Decimal('100')
        return round(base, 2)

    def __str__(self):
        return f'{self.project.code}-{self.plot_number}'


class Customer(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    PAYMENT_MODES = [
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
    ]

    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='bookings')
    plot = models.ForeignKey(Plot, on_delete=models.PROTECT, related_name='bookings')
    token_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES, default='upi')
    commission_pct = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default=STATUS_PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['plot'],
                condition=models.Q(status='pending'),
                name='uniq_open_booking_per_plot',
            ),
        ]

    def __str__(self):
        return f'{self.plot} / {self.customer} / {self.status}'


class Commission(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='commission')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tds_pct = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    tds_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    released = models.BooleanField(default=False)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.broker} × {self.amount}'


class CompanyProfile(models.Model):
    """Singleton row holding company details and the relationship manager."""

    name = models.CharField(max_length=200, default='InventoryOne Realty')
    support_email = models.EmailField(default='support@inventoryone.local')
    support_phone = models.CharField(max_length=20, default='+91 80 4000 1000')
    rm_name = models.CharField(max_length=120, default='Relationship Manager')
    rm_phone = models.CharField(max_length=20, default='+91 98800 11223')
    rm_email = models.EmailField(default='manager@inventoryone.local')

    class Meta:
        verbose_name_plural = 'Company profile'

    def __str__(self):
        return self.name

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Document(models.Model):
    """A stored file: broker KYC uploads, price lists, forms, demand letters."""

    KYC_PAN = 'kyc_pan'
    KYC_AADHAAR = 'kyc_aadhaar'
    KYC_GST = 'kyc_gst'
    KYC_CANCELLED_CHEQUE = 'kyc_cancelled_cheque'
    PRICE_LIST = 'price_list'
    FORM = 'form'
    DEMAND_LETTER = 'demand_letter'
    KIND_CHOICES = [
        (KYC_PAN, 'PAN card'),
        (KYC_AADHAAR, 'Aadhaar card'),
        (KYC_GST, 'GST certificate'),
        (KYC_CANCELLED_CHEQUE, 'Cancelled cheque'),
        (PRICE_LIST, 'Price list'),
        (FORM, 'Form'),
        (DEMAND_LETTER, 'Demand letter'),
    ]
    KYC_KINDS = [KYC_PAN, KYC_AADHAAR, KYC_GST, KYC_CANCELLED_CHEQUE]

    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='documents',
                                null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='documents',
                                 null=True, blank=True)
    kind = models.CharField(max_length=30, choices=KIND_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/%Y/%m/')
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_kyc(self):
        return self.kind in self.KYC_KINDS


class Notification(models.Model):
    KIND_PROJECT = 'project'
    KIND_SCHEME = 'scheme'
    KIND_BOOKING = 'booking'
    KIND_COMMISSION = 'commission'
    KIND_SYSTEM = 'system'
    KIND_CHOICES = [
        (KIND_PROJECT, 'New project'),
        (KIND_SCHEME, 'Scheme'),
        (KIND_BOOKING, 'Booking update'),
        (KIND_COMMISSION, 'Commission'),
        (KIND_SYSTEM, 'System'),
    ]

    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=KIND_SYSTEM)
    link = models.CharField(max_length=300, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['broker', 'read'])]

    def __str__(self):
        return self.title


class SupportTicket(models.Model):
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_RESOLVED, 'Resolved'),
    ]
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_NORMAL, 'Normal'),
        (PRIORITY_HIGH, 'High'),
    ]

    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} ({self.status})'


class AuditLog(models.Model):
    """Traceability record for approvals, releases and inventory changes (NFR-10)."""

    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='audit_entries')
    actor_name = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=60)
    entity_type = models.CharField(max_length=60, blank=True)
    entity_id = models.CharField(max_length=60, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['entity_type', 'entity_id'])]

    def __str__(self):
        return f'{self.action} by {self.actor_name or "system"}'
