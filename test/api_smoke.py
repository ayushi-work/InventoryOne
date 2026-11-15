#!/usr/bin/env python3
"""
End-to-end API smoke test for the InventoryOne Broker Web App.

Runs the full broker -> administrator workflow against a live server and
prints a PASS/FAIL line for every step. Exits non-zero if any step fails.

Usage:
    python test/api_smoke.py                       # uses http://127.0.0.1:8000
    python test/api_smoke.py --base http://host:8000
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
PASSED = 0
FAILED = 0


def request(method, path, body=None, token=None, form=None):
    """Perform an HTTP request and return (status, parsed_body)."""
    url = f"{BASE}{path}"
    headers = {}
    data = None

    if form is not None:
        boundary = "----InventoryOneSmokeBoundary"
        parts = []
        for key, value in form.items():
            if isinstance(value, tuple):
                filename, content, content_type = value
                parts.append(
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'
                    f"Content-Type: {content_type}\r\n\r\n".encode()
                )
                parts.append(content)
                parts.append(b"\r\n")
            else:
                parts.append(
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode()
                )
        parts.append(f"--{boundary}--\r\n".encode())
        data = b"".join(parts)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"

    if token:
        headers["Authorization"] = f"Token {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8", "replace")
            try:
                return response.status, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, raw
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", "replace")
        try:
            return err.code, json.loads(raw)
        except json.JSONDecodeError:
            return err.code, raw
    except urllib.error.URLError as err:
        return 0, str(err)


def check(label, condition, detail=""):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label} {detail}")


def login(email):
    """Log in with OTP and return the auth token."""
    status, body = request("POST", "/api/auth/request-otp/", {"email": email})
    if status != 200 or "dev_code" not in body:
        raise SystemExit(f"could not request OTP for {email}: {status} {body}")
    status, body = request("POST", "/api/auth/verify-otp/",
                           {"email": email, "code": body["dev_code"]})
    if status != 200:
        raise SystemExit(f"could not verify OTP for {email}: {status} {body}")
    return body["token"], body


def main():
    global BASE
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE)
    args = parser.parse_args()
    BASE = args.base.rstrip("/")

    print(f"Smoke testing {BASE}\n")

    print("[1] Health and authentication")
    status, body = request("GET", "/api/health/")
    check("health endpoint responds", status == 200, f"({status})")
    check("database is reachable", isinstance(body, dict) and body.get("database") == "up")

    broker_token, broker_session = login("broker@example.com")
    check("broker logs in with OTP", bool(broker_token))
    check("broker role is assigned", broker_session.get("role") == "broker")

    admin_token, admin_session = login("admin@inventoryone.local")
    check("admin logs in with OTP", bool(admin_token))
    check("admin role is assigned", admin_session.get("role") == "admin")

    print("\n[2] Role based access control")
    status, _ = request("GET", "/api/admin/stats/", token=broker_token)
    check("broker is blocked from admin endpoints", status == 403, f"(got {status})")
    status, _ = request("GET", "/api/projects/", token=admin_token)
    check("admin can read the API", status == 200, f"(got {status})")
    status, _ = request("GET", "/api/projects/")
    check("anonymous access is rejected", status == 401, f"(got {status})")

    print("\n[3] Projects and inventory")
    status, projects = request("GET", "/api/projects/", token=broker_token)
    check("project list loads", status == 200 and len(projects) > 0, f"(got {status})")
    project = projects[0]
    check("availability counts are present",
          "available" in project and "total_plots" in project)

    status, detail = request("GET", f"/api/projects/{project['id']}/", token=broker_token)
    check("project detail loads", status == 200, f"(got {status})")
    check("plots are returned", len(detail.get("plots", [])) > 0)
    available = [p for p in detail["plots"] if p["status"] == "available"]
    check("at least one plot is available", len(available) > 0)

    print("\n[4] Customers")
    status, customer = request("POST", "/api/customers/", {
        "name": "Smoke Test Customer", "phone": "9000001234",
        "email": "smoke@example.com", "address": "Bengaluru",
    }, token=broker_token)
    check("customer is registered", status == 201, f"(got {status})")
    status, customers = request("GET", "/api/customers/", token=broker_token)
    check("customer list loads", status == 200 and len(customers) > 0)

    print("\n[5] Booking workflow")
    plot = available[0]
    status, booking = request("POST", "/api/bookings/", {
        "customer": customer["id"], "plot": plot["id"],
        "token_amount": 250000, "payment_mode": "upi",
    }, token=broker_token)
    check("booking is created", status == 201, f"(got {status})")
    check("booking starts as pending", booking.get("status") == "pending")

    status, _ = request("POST", "/api/bookings/", {
        "customer": customer["id"], "plot": plot["id"],
        "token_amount": 250000, "payment_mode": "upi",
    }, token=broker_token)
    check("double booking is rejected", status == 409, f"(got {status})")

    status, detail = request("GET", f"/api/projects/{project['id']}/", token=broker_token)
    held = [p for p in detail["plots"] if p["id"] == plot["id"]][0]
    check("plot moved to on hold", held["status"] == "on_hold", held["status"])

    print("\n[6] Administrator approval")
    status, decided = request("POST", f"/api/admin/bookings/{booking['id']}/decide/",
                               {"action": "approve"}, token=admin_token)
    check("booking is approved", status == 200, f"(got {status})")
    check("booking status is approved", decided.get("status") == "approved")
    check("commission was created", decided.get("commission") is not None)

    status, detail = request("GET", f"/api/projects/{project['id']}/", token=broker_token)
    sold = [p for p in detail["plots"] if p["id"] == plot["id"]][0]
    check("plot moved to sold", sold["status"] == "sold", sold["status"])

    print("\n[7] Commission ledger")
    status, commissions = request("GET", "/api/commissions/", token=broker_token)
    check("commission list loads", status == 200 and len(commissions) > 0)
    latest = commissions[0]
    gross = float(latest["amount"])
    tds = float(latest["tds_amount"])
    net = float(latest["net_amount"])
    check("TDS is 10% of gross", abs(tds - gross * 0.1) < 0.02, f"{tds} vs {gross * 0.1}")
    check("net equals gross minus TDS", abs(net - (gross - tds)) < 0.02)

    status, released = request("POST",
                               f"/api/admin/commissions/{latest['id']}/release/",
                               token=admin_token)
    check("commission is released", status == 200 and released.get("released") is True,
          f"(got {status})")

    print("\n[8] Documents")
    status, docs = request("POST", "/api/documents/", form={
        "kind": "kyc_pan", "title": "Smoke PAN",
        "file": ("smoke.txt", b"%PDF-1.4 smoke", "application/pdf"),
    }, token=broker_token)
    check("KYC document uploads", status == 201, f"(got {status})")

    status, price_list = request("POST", f"/api/projects/{project['id']}/price-list/",
                                  token=broker_token)
    check("price list is generated", status == 201, f"(got {status})")

    status, letter = request("POST", f"/api/bookings/{booking['id']}/demand-letter/",
                             token=broker_token)
    check("demand letter is generated", status == 201, f"(got {status})")

    print("\n[9] Notifications")
    status, notifications = request("GET", "/api/notifications/", token=broker_token)
    check("notification list loads", status == 200 and len(notifications) > 0)
    status, unread = request("GET", "/api/notifications/unread-count/", token=broker_token)
    check("unread count is returned", status == 200 and "unread" in unread)
    status, _ = request("POST", "/api/notifications/mark-read/", {}, token=broker_token)
    check("notifications can be marked read", status == 200)

    print("\n[10] Support")
    status, ticket = request("POST", "/api/tickets/", {
        "subject": "Smoke test ticket", "message": "Checking the support flow",
        "priority": "normal",
    }, token=broker_token)
    check("support ticket is raised", status == 201, f"(got {status})")

    status, company = request("GET", "/api/company/", token=broker_token)
    check("company profile loads", status == 200 and "rm_phone" in company, f"(got {status})")

    status, resolved = request("POST", "/api/admin/tickets/", {
        "id": ticket["id"], "status": "resolved", "response": "Handled by the smoke test.",
    }, token=admin_token)
    check("admin resolves the ticket", status == 200 and resolved.get("status") == "resolved",
          f"(got {status})")

    print("\n[11] Administration")
    status, stats = request("GET", "/api/admin/stats/", token=admin_token)
    check("admin stats load", status == 200 and "pending_bookings" in stats, f"(got {status})")

    status, audit = request("GET", "/api/admin/audit-log/", token=admin_token)
    check("audit log is populated", status == 200 and len(audit) > 0, f"(got {status})")

    status, brokers = request("GET", "/api/admin/brokers/", token=admin_token)
    check("broker list loads", status == 200 and len(brokers) > 0)

    status, broadcast = request("POST", "/api/admin/broadcast/", {
        "title": "Smoke test broadcast", "body": "Checking fan-out", "kind": "scheme",
    }, token=admin_token)
    check("broadcast reaches every broker", status == 201 and broadcast.get("sent", 0) > 0)

    print(f"\n{'=' * 52}")
    print(f"  {PASSED} passed, {FAILED} failed")
    print(f"{'=' * 52}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
