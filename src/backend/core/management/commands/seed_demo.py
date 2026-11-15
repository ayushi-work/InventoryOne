"""Seed the database with demo projects, plots, brokers and bookings."""
import random
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Booking, Broker, Commission, Customer, Plot, Project

PROJECTS = [
    {
        'name': 'Green Valley Heights',
        'code': 'GVH',
        'location': 'Whitefield, Bengaluru',
        'description': 'RERA-approved residential layout with 24 plots across two blocks.',
        'bsp': Decimal('4850'),
        'sizes': [Decimal('200'), Decimal('250'), Decimal('300')],
    },
    {
        'name': 'Palm Grove Residency',
        'code': 'PGR',
        'location': 'Sarjapur Road, Bengaluru',
        'description': 'Gated community project with premium east-facing corner plots.',
        'bsp': Decimal('5600'),
        'sizes': [Decimal('300'), Decimal('400'), Decimal('450')],
    },
    {
        'name': 'Lake View Plots',
        'code': 'LVP',
        'location': 'Hennur Main Road, Bengaluru',
        'description': 'Lake-facing plots with limited inventory and high demand.',
        'bsp': Decimal('7200'),
        'sizes': [Decimal('400'), Decimal('600')],
    },
]

CUSTOMERS = [
    ('Ramesh Kumar', 'ramesh@example.com', '9845012345'),
    ('Priya Sharma', 'priya@example.com', '9845012346'),
    ('Anand Nair', 'anand@example.com', '9845012347'),
    ('Divya Menon', 'divya@example.com', '9845012348'),
    ('Suresh Iyer', 'suresh@example.com', '9845012349'),
]

FACINGS = ['E', 'W', 'N', 'S', 'NE', 'NW', 'SE', 'SW']


class Command(BaseCommand):
    help = 'Seed demo data for the InventoryOne Broker Web App.'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true',
                            help='Delete existing core data before seeding.')

    def handle(self, *args, **options):
        random.seed(42)

        if options['flush']:
            Commission.objects.all().delete()
            Booking.objects.all().delete()
            Customer.objects.all().delete()
            Plot.objects.all().delete()
            Project.objects.all().delete()
            Broker.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write('Existing core data removed.')

        admin = self._create_admin()
        broker, other_broker = self._create_brokers()

        projects = []
        for spec in PROJECTS:
            project, _ = Project.objects.get_or_create(
                code=spec['code'],
                defaults={
                    'name': spec['name'],
                    'location': spec['location'],
                    'description': spec['description'],
                    'status': Project.STATUS_ACTIVE,
                },
            )
            projects.append((project, spec))
            self._create_plots(project, spec)

        customers = self._create_customers(broker)
        other_customers = self._create_customers(other_broker, offset=5)

        self._create_bookings(broker, customers, projects)
        self._create_bookings(other_broker, other_customers, projects)

        self.stdout.write(self.style.SUCCESS(
            'Seed complete: '
            f'{Project.objects.count()} projects, {Plot.objects.count()} plots, '
            f'{Broker.objects.count()} brokers, {Customer.objects.count()} customers, '
            f'{Booking.objects.count()} bookings, {Commission.objects.count()} commissions.'
        ))
        self.stdout.write(f'Admin login: {admin.username} / admin123')
        self.stdout.write('Broker login: broker@example.com (OTP, dev code shown in response)')

    # -- helpers ----------------------------------------------------------
    def _create_admin(self):
        admin, created = User.objects.get_or_create(
            username='admin@inventoryone.local',
            defaults={'email': 'admin@inventoryone.local', 'first_name': 'Company',
                      'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        Broker.objects.get_or_create(user=admin, defaults={'kyc_status': Broker.KYC_APPROVED})
        return admin

    def _create_brokers(self):
        broker = self._broker('broker@example.com', 'Ravi', Broker.KYC_APPROVED,
                               pan='ABCDE1234F', rera='RERA-KA-2024-001')
        other = self._broker('priya.broker@example.com', 'Priya', Broker.KYC_PENDING,
                             pan='XYZAB9876K', rera='RERA-KA-2024-002')
        return broker, other

    def _broker(self, email, name, kyc_status, pan='', rera=''):
        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': name},
        )
        if created:
            user.set_unusable_password()
            user.save()
        broker, _ = Broker.objects.get_or_create(
            user=user,
            defaults={
                'phone': '9845000000',
                'kyc_status': kyc_status,
                'pan_number': pan,
                'rera_number': rera,
                'aadhaar_number': 'XXXX-XXXX-1234',
                'gst_number': '29ABCDE1234F1Z5',
                'bank_account': '50100234567890',
                'ifsc': 'HDFC0001234',
                'agreement_accepted': True,
            },
        )
        return broker

    def _create_plots(self, project, spec):
        if project.plots.exists():
            return
        rows = 4
        cols = 6
        for r in range(rows):
            for c in range(cols):
                number = f'{r * cols + c + 1:03d}'
                size = random.choice(spec['sizes'])
                plc = random.choice([0, 0, 5, 10])
                discount = random.choice([0, 0, 3, 5])
                Plot.objects.create(
                    project=project,
                    plot_number=number,
                    size_sq_yds=size,
                    facing=random.choice(FACINGS),
                    status=Plot.STATUS_AVAILABLE,
                    bsp=spec['bsp'],
                    plc_pct=Decimal(plc),
                    discount_pct=Decimal(discount),
                )

    def _create_customers(self, broker, offset=0):
        customers = []
        for i, (name, email, phone) in enumerate(CUSTOMERS):
            customer, _ = Customer.objects.get_or_create(
                broker=broker,
                email=email,
                defaults={'name': name, 'phone': phone,
                          'address': f'{name}, Bengaluru, Karnataka'},
            )
            customers.append(customer)
        return customers

    def _create_bookings(self, broker, customers, projects):
        if broker.bookings.exists():
            return

        # One pending booking -> admin approves it (creates a commission).
        project, spec = projects[0]
        plot = project.plots.filter(status=Plot.STATUS_AVAILABLE).first()
        if plot and customers:
            customer = customers[0]
            booking = Booking.objects.create(
                broker=broker,
                customer=customer,
                plot=plot,
                token_amount=Decimal('250000'),
                payment_mode='upi',
                status=Booking.STATUS_PENDING,
            )
            plot.status = Plot.STATUS_ON_HOLD
            plot.save(update_fields=['status'])

            # Approve it so the seeded data shows a commission too.
            booking.status = Booking.STATUS_APPROVED
            booking.decided_at = timezone.now()
            booking.save()
            plot.status = Plot.STATUS_SOLD
            plot.save(update_fields=['status'])
            gross = plot.total_cost * booking.commission_pct / Decimal(100)
            tds = gross * Decimal(10) / Decimal(100)
            Commission.objects.create(
                booking=booking,
                broker=broker,
                amount=round(gross, 2),
                tds_pct=Decimal(10),
                tds_amount=round(tds, 2),
                net_amount=round(gross - tds, 2),
            )

        # A second pending booking for the admin queue.
        project2, _ = projects[1]
        plot2 = project2.plots.filter(status=Plot.STATUS_AVAILABLE).first()
        if plot2 and len(customers) > 1:
            Booking.objects.create(
                broker=broker,
                customer=customers[1],
                plot=plot2,
                token_amount=Decimal('500000'),
                payment_mode='bank',
                status=Booking.STATUS_PENDING,
            )
            plot2.status = Plot.STATUS_ON_HOLD
            plot2.save(update_fields=['status'])
