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
