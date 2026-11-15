"""API tests for the InventoryOne Broker Web App."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import (
    AuditLog,
    Booking,
    Broker,
    Commission,
    CompanyProfile,
    Customer,
    Document,
    Notification,
    Plot,
    Project,
    SupportTicket,
)


def make_user(email, staff=False):
    user = User.objects.create_user(username=email, email=email, password="x")
    if staff:
        user.is_staff = True
        user.save()
    Broker.objects.create(user=user)
    return user


def api_client_for(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + Token.objects.create(user=user).key)
    return client


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

    def test_otp_requires_email(self):
        res = self.client.post(reverse("request_otp"), {}, format="json")
        self.assertEqual(res.status_code, 400)


class ProjectTests(TestCase):
    def setUp(self):
        self.user = make_user("broker@example.com")
        self.client = api_client_for(self.user)
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

    def test_unknown_project_returns_404(self):
        res = self.client.get(reverse("project_detail", args=[999]))
        self.assertEqual(res.status_code, 404)

    def test_total_cost_applies_plc_and_discount(self):
        plot = Plot.objects.create(
            project=self.project, plot_number="002", size_sq_yds=Decimal("100"),
            facing="N", bsp=Decimal("1000"), plc_pct=Decimal("10"), discount_pct=Decimal("5"),
        )
        # 100 * 1000 = 100000, +10% = 110000, -5% = 104500
        self.assertEqual(plot.total_cost, Decimal("104500.00"))


class BookingFlowTests(TestCase):
    def setUp(self):
        self.user = make_user("broker@example.com")
        self.client = api_client_for(self.user)
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
        first = self.client.post(reverse("bookings"), payload, format="json")
        self.assertEqual(first.status_code, 201, first.data)
        self.plot.refresh_from_db()
        self.assertEqual(self.plot.status, Plot.STATUS_ON_HOLD)
        res = self.client.post(reverse("bookings"), payload, format="json")
        self.assertIn(res.status_code, (400, 409), res.data)

    def test_booking_creates_a_notification(self):
        self.client.post(
            reverse("bookings"),
            {"customer": self.customer.pk, "plot": self.plot.pk,
             "token_amount": "100000", "payment_mode": "upi"},
            format="json",
        )
        self.assertTrue(
            Notification.objects.filter(broker=self.user.broker, kind=Notification.KIND_BOOKING).exists()
        )


class AdminTests(TestCase):
    def setUp(self):
        self.broker_user = make_user("broker@example.com")
        self.admin_user = make_user("admin@inventoryone.local", staff=True)
        self.admin = api_client_for(self.admin_user)
        self.broker = api_client_for(self.broker_user)

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
        self.assertEqual(self.broker.get(reverse("admin_projects")).status_code, 403)

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

    def test_booking_cannot_be_decided_twice(self):
        self.admin.post(
            reverse("admin_decide_booking", args=[self.booking.pk]), {"action": "approve"},
            format="json",
        )
        res = self.admin.post(
            reverse("admin_decide_booking", args=[self.booking.pk]), {"action": "reject"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_commission_release_is_recorded(self):
        self.admin.post(
            reverse("admin_decide_booking", args=[self.booking.pk]), {"action": "approve"},
            format="json",
        )
        commission = Commission.objects.get(booking=self.booking)
        res = self.admin.post(reverse("admin_release_commission", args=[commission.pk]))
        self.assertEqual(res.status_code, 200)
        commission.refresh_from_db()
        self.assertTrue(commission.released)
        self.assertIsNotNone(commission.released_at)

    def test_decision_writes_an_audit_entry(self):
        self.admin.post(
            reverse("admin_decide_booking", args=[self.booking.pk]), {"action": "approve"},
            format="json",
        )
        self.assertTrue(AuditLog.objects.filter(action="booking.approved").exists())

    def test_admin_can_create_a_project_and_plots(self):
        res = self.admin.post(
            reverse("admin_projects"),
            {"name": "New Project", "code": "NP9", "location": "Whitefield",
             "status": Project.STATUS_ACTIVE, "description": "Test"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        project = Project.objects.get(code="NP9")

        res = self.admin.post(
            reverse("admin_plots", args=[project.pk]),
            {"plots": [
                {"plot_number": "001", "size_sq_yds": "200", "facing": "E",
                 "status": Plot.STATUS_AVAILABLE, "bsp": "4500"},
                {"plot_number": "002", "size_sq_yds": "300", "facing": "W",
                 "status": Plot.STATUS_AVAILABLE, "bsp": "4500"},
            ]},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(project.plots.count(), 2)

    def test_bulk_plot_creation_rejects_duplicates(self):
        res = self.admin.post(
            reverse("admin_plots", args=[self.project.pk]),
            {"plots": [
                {"plot_number": "001", "size_sq_yds": "200", "facing": "E", "bsp": "4500"},
                {"plot_number": "001", "size_sq_yds": "300", "facing": "W", "bsp": "4500"},
            ]},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_admin_broadcast_notifies_all_brokers(self):
        res = self.admin.post(
            reverse("admin_broadcast"),
            {"title": "Festive scheme", "body": "3% extra discount", "kind": "scheme"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["sent"], Broker.objects.count())

    def test_admin_can_approve_kyc(self):
        broker = self.broker_user.broker
        broker.kyc_status = Broker.KYC_PENDING
        broker.save()
        res = self.admin.post(
            reverse("admin_brokers"), {"id": broker.id, "kyc_status": Broker.KYC_APPROVED},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        broker.refresh_from_db()
        self.assertEqual(broker.kyc_status, Broker.KYC_APPROVED)

    def test_admin_can_resolve_a_ticket(self):
        ticket = SupportTicket.objects.create(
            broker=self.broker_user.broker, subject="Help", message="Please help")
        res = self.admin.post(
            reverse("admin_tickets"),
            {"id": ticket.id, "status": SupportTicket.STATUS_RESOLVED, "response": "Done"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, SupportTicket.STATUS_RESOLVED)
        self.assertIsNotNone(ticket.resolved_at)


class DocumentTests(TestCase):
    def setUp(self):
        self.user = make_user("broker@example.com")
        self.client = api_client_for(self.user)
        self.project = Project.objects.create(name="P", code="P1", status=Project.STATUS_ACTIVE)
        self.plot = Plot.objects.create(
            project=self.project, plot_number="001", size_sq_yds=Decimal("200"),
            facing="E", bsp=Decimal("5000"),
        )
        self.customer = Customer.objects.create(
            broker=self.user.broker, name="C", phone="9"
        )
        self.booking = Booking.objects.create(
            broker=self.user.broker, customer=self.customer, plot=self.plot,
            token_amount=Decimal("100000"), payment_mode="upi",
        )

    def test_kyc_upload_creates_a_document(self):
        upload = SimpleUploadedFile("pan.pdf", b"%PDF-1.4 fake", content_type="application/pdf")
        res = self.client.post(
            reverse("document_list"),
            {"kind": Document.KYC_PAN, "title": "PAN card", "file": upload},
            format="multipart",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Document.objects.filter(broker=self.user.broker).count(), 1)

    def test_upload_rejects_non_kyc_kind(self):
        upload = SimpleUploadedFile("x.pdf", b"data", content_type="application/pdf")
        res = self.client.post(
            reverse("document_list"),
            {"kind": Document.PRICE_LIST, "file": upload},
            format="multipart",
        )
        self.assertEqual(res.status_code, 400)

    def test_price_list_is_generated(self):
        res = self.client.post(reverse("generate_price_list", args=[self.project.pk]))
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Document.objects.filter(kind=Document.PRICE_LIST).count(), 1)

    def test_demand_letter_requires_approved_booking(self):
        res = self.client.post(reverse("generate_demand_letter", args=[self.booking.pk]))
        self.assertEqual(res.status_code, 400)

        self.booking.status = Booking.STATUS_APPROVED
        self.booking.save()
        res = self.client.post(reverse("generate_demand_letter", args=[self.booking.pk]))
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Document.objects.filter(kind=Document.DEMAND_LETTER).count(), 1)

    def test_kyc_summary_is_downloadable(self):
        res = self.client.get(reverse("kyc_summary"))
        self.assertEqual(res.status_code, 200)
        self.assertIn("attachment", res["Content-Disposition"])

    def test_document_download_requires_ownership(self):
        other = make_user("other@example.com")
        other_client = api_client_for(other)
        doc = Document.objects.create(
            broker=self.user.broker, kind=Document.KYC_PAN, title="PAN",
            content_type="application/pdf",
        )
        doc.file.save("pan.pdf", SimpleUploadedFile("pan.pdf", b"data"), save=True)
        res = other_client.get(reverse("document_download", args=[doc.pk]))
        self.assertEqual(res.status_code, 403)


class NotificationTests(TestCase):
    def setUp(self):
        self.user = make_user("broker@example.com")
        self.client = api_client_for(self.user)

    def test_notification_list_and_unread_count(self):
        Notification.objects.create(broker=self.user.broker, title="A", body="B")
        Notification.objects.create(broker=self.user.broker, title="C", body="D", read=True)

        res = self.client.get(reverse("notification_list"))
        self.assertEqual(len(res.data), 2)

        res = self.client.get(reverse("notification_unread_count"))
        self.assertEqual(res.data["unread"], 1)

    def test_mark_read_marks_all(self):
        Notification.objects.create(broker=self.user.broker, title="A")
        Notification.objects.create(broker=self.user.broker, title="B")
        res = self.client.post(reverse("notification_mark_read"), {}, format="json")
        self.assertEqual(res.data["marked_read"], 2)
        self.assertEqual(
            self.user.broker.notifications.filter(read=False).count(), 0
        )

    def test_notifications_are_scoped_to_the_broker(self):
        other = make_user("other@example.com")
        Notification.objects.create(broker=other.broker, title="Not mine")
        res = self.client.get(reverse("notification_list"))
        self.assertEqual(len(res.data), 0)


class SupportTests(TestCase):
    def setUp(self):
        self.user = make_user("broker@example.com")
        self.client = api_client_for(self.user)

    def test_create_ticket(self):
        res = self.client.post(
            reverse("tickets"),
            {"subject": "Need help", "message": "Payment link please",
             "priority": SupportTicket.PRIORITY_NORMAL},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(SupportTicket.objects.filter(broker=self.user.broker).count(), 1)

    def test_company_profile_is_available(self):
        res = self.client.get(reverse("company_profile"))
        self.assertEqual(res.status_code, 200)
        self.assertIn("rm_phone", res.data)
