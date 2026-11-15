"""API tests for the InventoryOne Broker Web App."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Booking, Broker, Commission, Customer, Plot, Project


def make_user(email, staff=False):
    user = User.objects.create_user(username=email, email=email, password="x")
    if staff:
        user.is_staff = True
        user.save()
    Broker.objects.create(user=user)
    return user


@override_settings(OTP_DEBUG_MODE=True)
class AuthTests(TestCase):
    def test_request_otp_creates_broker_and_code(self):
        res = self.client.post(
            reverse("request_otp"), {"email": "new@example.com"}, format="json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("dev_code", res.data)
        self.assertTrue(Broker.objects.filter(user__username="new@example.com").exists())

    def test_verify_otp_returns_token(self):
        res = self.client.post(
            reverse("request_otp"), {"email": "new@example.com"}, format="json"
        )
        code = res.data["dev_code"]
        res = self.client.post(
            reverse("verify_otp"), {"email": "new@example.com", "code": code}, format="json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["role"], "broker")

    def test_verify_otp_rejects_wrong_code(self):
        self.client.post(reverse("request_otp"), {"email": "a@b.com"}, format="json")
        res = self.client.post(
            reverse("verify_otp"), {"email": "a@b.com", "code": "000000"}, format="json"
        )
        self.assertEqual(res.status_code, 400)


class ProjectTests(TestCase):
    def setUp(self):
        self.user = make_user("broker@example.com")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + Token.objects.create(user=self.user).key)
        self.project = Project.objects.create(name="Test", code="TST", status=Project.STATUS_ACTIVE)
        Plot.objects.create(
            project=self.project, plot_number="001", size_sq_yds=Decimal("200"),
            facing="E", bsp=Decimal("5000"),
        )

    def test_project_list_returns_counts(self):
        res = self.client.get(reverse("project_list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data[0]["available"], 1)

    def test_project_detail_returns_plots(self):
        res = self.client.get(reverse("project_detail", args=[self.project.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["plots"]), 1)
        self.assertEqual(res.data["plots"][0]["total_cost"], Decimal("1000000.00"))


class BookingFlowTests(TestCase):
    def setUp(self):
        self.user = make_user("broker@example.com")
        self.token = Token.objects.create(user=self.user).key
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        self.project = Project.objects.create(name="Test", code="TST", status=Project.STATUS_ACTIVE)
        self.plot = Plot.objects.create(
            project=self.project, plot_number="001", size_sq_yds=Decimal("200"),
            facing="E", bsp=Decimal("5000"),
        )
        self.customer = Customer.objects.create(
            broker=self.user.broker, name="Cust", phone="9999999999"
        )

    def test_create_booking_holds_plot(self):
        res = self.client.post(
            reverse("bookings"),
            {"customer": self.customer.pk, "plot": self.plot.pk,
             "token_amount": "100000", "payment_mode": "upi"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["status"], Booking.STATUS_PENDING)
        self.plot.refresh_from_db()
        self.assertEqual(self.plot.status, Plot.STATUS_ON_HOLD)

    def test_double_booking_is_rejected(self):
        payload = {"customer": self.customer.pk, "plot": self.plot.pk,
                   "token_amount": "100000", "payment_mode": "upi"}
        self.client.post(reverse("bookings"), payload, format="json")
        res = self.client.post(reverse("bookings"), payload, format="json")
        self.assertEqual(res.status_code, 409)


class AdminTests(TestCase):
    def setUp(self):
        self.broker_user = make_user("broker@example.com")
        self.admin_user = make_user("admin@inventoryone.local", staff=True)
        self.admin = APIClient()
        self.admin.credentials(
            HTTP_AUTHORIZATION="Token " + Token.objects.create(user=self.admin_user).key
        )
        self.broker = APIClient()
        self.broker.credentials(
            HTTP_AUTHORIZATION="Token " + Token.objects.create(user=self.broker_user).key
        )

        self.project = Project.objects.create(name="P", code="P1", status=Project.STATUS_ACTIVE)
        self.plot = Plot.objects.create(
            project=self.project, plot_number="001", size_sq_yds=Decimal("200"),
            facing="E", bsp=Decimal("5000"),
        )
        self.customer = Customer.objects.create(
            broker=self.broker_user.broker, name="C", phone="9"
        )
        self.booking = Booking.objects.create(
            broker=self.broker_user.broker, customer=self.customer, plot=self.plot,
            token_amount=Decimal("100000"), payment_mode="upi",
        )

    def test_broker_cannot_access_admin_endpoints(self):
        self.assertEqual(self.broker.get(reverse("admin_stats")).status_code, 403)

    def test_approval_marks_plot_sold_and_creates_commission(self):
        res = self.admin.post(
            reverse("admin_decide_booking", args=[self.booking.pk]), {"action": "approve"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.booking.refresh_from_db()
        self.plot.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.STATUS_APPROVED)
        self.assertEqual(self.plot.status, Plot.STATUS_SOLD)

        commission = Commission.objects.get(booking=self.booking)
        self.assertEqual(commission.amount, Decimal("20000.00"))  # 2% of 1,000,000
        self.assertEqual(commission.tds_amount, Decimal("2000.00"))
        self.assertEqual(commission.net_amount, Decimal("18000.00"))

    def test_rejection_releases_plot(self):
        res = self.admin.post(
            reverse("admin_decide_booking", args=[self.booking.pk]), {"action": "reject"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.plot.refresh_from_db()
        self.assertEqual(self.plot.status, Plot.STATUS_AVAILABLE)
        self.assertFalse(Commission.objects.filter(booking=self.booking).exists())
