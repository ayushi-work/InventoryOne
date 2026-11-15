# Test Cases — InventoryOne Broker Web App

This directory holds the **manual test cases** and the **API smoke test** used to
validate a release. The automated unit/integration suite lives with the code in
`src/backend/core/tests.py` and runs with `python manage.py test core`.

---

## 1. Test strategy

| Level                | Scope                                                  | Where it lives                     |
| -------------------- | ------------------------------------------------------ | ---------------------------------- |
| Unit                 | Commission arithmetic, plot pricing, OTP expiry        | `core/tests.py`                    |
| Integration / API    | Every endpoint, happy path and error path              | `core/tests.py`                    |
| System               | Full broker → administrator workflow against a live API | `test/api_smoke.py`                |
| Manual / UAT         | UI behaviour, role separation, live updates             | `test/test-cases.md` (this file)   |
| Regression           | The whole suite on every push                          | `.github/workflows/ci.yml`         |

---

## 2. Automated test coverage

`src/backend/core/tests.py` — **33 tests** across 7 test classes:

| Class              | Tests | Covers                                                  |
| ------------------ | ----- | ------------------------------------------------------- |
| `AuthTests`        | 4     | OTP request, verification, wrong code, missing email     |
| `ProjectTests`     | 5     | Project listing, counts, plot detail, 404, PLC pricing   |
| `BookingFlowTests` | 3     | Booking creation, plot hold, double-booking rejection    |
| `AdminTests`       | 9     | RBAC, approve/reject, commission maths, release, audit, project + bulk plot CRUD, duplicate detection, broadcast, KYC approval, ticket resolution |
| `DocumentTests`    | 6     | KYC upload, kind validation, price list, demand letter, KYC summary, download ownership |
| `NotificationTests`| 3     | Listing, unread count, mark read, broker scoping        |
| `SupportTests`     | 2     | Ticket creation, company profile                        |

Run them with:

```bash
cd src/backend
python manage.py test core --verbosity 2
```

---

## 3. Manual test cases

### TC-01 — Broker registration via OTP

| | |
| --- | --- |
| **Pre-condition** | The broker is not yet registered |
| **Steps** | 1. Open `/` → 2. Enter a new e-mail → 3. Click **Send OTP** → 4. Enter the OTP → 5. Click **Verify & Login** |
| **Expected result** | A broker profile is created automatically, the dashboard opens and the nav shows the broker links |
| **Actual result** | |

### TC-02 — Invalid OTP is rejected

| | |
| --- | --- |
| **Pre-condition** | A valid OTP has just been issued |
| **Steps** | 1. Enter a wrong OTP → 2. Click **Verify & Login** |
| **Expected result** | "Invalid or expired OTP" is shown and no session is created |
| **Actual result** | |

### TC-03 — Live availability colour coding

| | |
| --- | --- |
| **Pre-condition** | The broker is logged in and at least one project exists |
| **Steps** | 1. Open **Projects** → 2. Open a project → 3. Inspect the plot grid |
| **Expected result** | Available plots have a green edge, on-hold plots amber, sold plots red; the legend matches |
| **Actual result** | |

### TC-04 — Plot details and pricing

| | |
| --- | --- |
| **Pre-condition** | The broker is logged in |
| **Steps** | 1. Click any plot in the grid |
| **Expected result** | The drawer shows plot number, size, facing, BSP, PLC, discount, status and the computed total cost |
| **Actual result** | |

### TC-05 — Register a customer

| | |
| --- | --- |
| **Pre-condition** | The broker is logged in |
| **Steps** | 1. Open **Customers** → 2. Fill in name and phone → 3. Submit |
| **Expected result** | The customer appears in the table with the registration date |
| **Actual result** | |

### TC-06 — Raise a booking request

| | |
| --- | --- |
| **Pre-condition** | A customer is registered and a plot is available |
| **Steps** | 1. Open a project → 2. Click an available plot → 3. Select the customer → 4. Enter a token amount and payment mode → 5. Submit |
| **Expected result** | "Booking request raised" is shown, the plot turns amber (on hold) and a booking appears under **Bookings** with status *pending* |
| **Actual result** | |

### TC-07 — Double booking is prevented

| | |
| --- | --- |
| **Pre-condition** | A plot already has a pending booking |
| **Steps** | 1. Attempt to raise a second booking on the same plot (via a second broker or the API) |
| **Expected result** | The request is rejected with HTTP 409 — the plot is never double-booked |
| **Actual result** | |

### TC-08 — Administrator approves a booking

| | |
| --- | --- |
| **Pre-condition** | A pending booking exists |
| **Steps** | 1. Sign in as `admin@inventoryone.local` → 2. Open **Admin → Bookings** → 3. Click **Approve** |
| **Expected result** | The booking becomes *approved*, the plot turns red (sold), a commission is created and the broker is notified |
| **Actual result** | |

### TC-09 — Administrator rejects a booking

| | |
| --- | --- |
| **Pre-condition** | A pending booking exists |
| **Steps** | 1. Open **Admin → Bookings** → 2. Click **Reject** |
| **Expected result** | The booking becomes *rejected* and the plot returns to *available* |
| **Actual result** | |

### TC-10 — Commission and TDS

| | |
| --- | --- |
| **Pre-condition** | A booking has been approved |
| **Steps** | 1. Open **Commissions** as the broker |
| **Expected result** | Gross = 2 % of the plot total, TDS = 10 % of gross, and the net payable is shown correctly |
| **Actual result** | |

### TC-11 — Role-based access control

| | |
| --- | --- |
| **Pre-condition** | Signed in as a broker |
| **Steps** | 1. Request `/api/admin/stats/` directly |
| **Expected result** | HTTP 403 — administrative functions are not reachable by brokers |
| **Actual result** | |

### TC-12 — KYC document upload

| | |
| --- | --- |
| **Pre-condition** | Signed in as a broker |
| **Steps** | 1. Open **Documents** → 2. Choose a document type → 3. Pick a PDF → 4. Click **Upload** |
| **Expected result** | The file appears under *My KYC files* with its size and a working download link |
| **Actual result** | |

### TC-13 — Price list PDF

| | |
| --- | --- |
| **Pre-condition** | At least one project exists |
| **Steps** | 1. Open **Documents** → 2. Pick a project → 3. Click **Generate PDF** |
| **Expected result** | A downloadable PDF price list is produced listing every plot with area, facing, rate and total |
| **Actual result** | |

### TC-14 — Demand letter

| | |
| --- | --- |
| **Pre-condition** | A booking has been approved |
| **Steps** | 1. Open **Bookings** → 2. Click **Demand letter** |
| **Expected result** | A PDF opens with the booking reference, customer, plot details, token amount and relationship manager contact |
| **Actual result** | |

### TC-15 — Notifications

| | |
| --- | --- |
| **Pre-condition** | A booking has been approved or rejected |
| **Steps** | 1. Look at the bell in the nav → 2. Open **Notifications** |
| **Expected result** | The unread badge shows the count and the booking update appears in the feed |
| **Actual result** | |

### TC-16 — Support ticket

| | |
| --- | --- |
| **Pre-condition** | Signed in as a broker |
| **Steps** | 1. Open **Support** → 2. Enter a subject and message → 3. Submit |
| **Expected result** | The ticket is created with status *open* and appears under *My tickets* |
| **Actual result** | |

### TC-17 — Admin responds to a ticket

| | |
| --- | --- |
| **Pre-condition** | A broker raised a ticket |
| **Steps** | 1. Sign in as admin → 2. Open **Admin → Tickets** → 3. Type a response → 4. Click **Resolve** |
| **Expected result** | The ticket becomes *resolved* and the broker sees the response and a notification |
| **Actual result** | |

### TC-18 — Admin manages projects and plots

| | |
| --- | --- |
| **Pre-condition** | Signed in as admin |
| **Steps** | 1. Open **Admin → Projects** → 2. Create a project → 3. Add a plot → 4. Change the plot status |
| **Expected result** | The project appears in the list with live counts and the new plot is editable |
| **Actual result** | |

### TC-19 — Admin broadcasts a notification

| | |
| --- | --- |
| **Pre-condition** | Signed in as admin |
| **Steps** | 1. Open **Admin → Brokers** → 2. Enter a title and message → 3. Click **Send to all brokers** |
| **Expected result** | Every broker receives the notification; the admin sees the recipient count |
| **Actual result** | |

### TC-20 — Audit trail

| | |
| --- | --- |
| **Pre-condition** | At least one approval has happened |
| **Steps** | 1. Open **Admin → Audit** |
| **Expected result** | Each approval, release and inventory change is listed with actor, action, entity and timestamp |
| **Actual result** | |

### TC-21 — Live updates over WebSocket

| | |
| --- | --- |
| **Pre-condition** | Two browsers — one as broker, one as admin |
| **Steps** | 1. Broker opens a project → 2. Admin approves a booking on that plot → 3. Watch the broker's grid |
| **Expected result** | The broker's plot tile changes colour without a manual refresh; the "Live updates on" indicator is shown |
| **Actual result** | |

### TC-22 — Audit trail on the admin dashboard

| | |
| --- | --- |
| **Pre-condition** | Signed in as admin |
| **Steps** | 1. Open **Admin → Dashboard** → 2. Confirm the statistics tiles |
| **Expected result** | Broker, KYC, plot, booking, commission and ticket counts match the database |
| **Actual result** | |

---

## 4. Exit criteria

A release is acceptable when:

1. `python manage.py test core` passes with 0 failures and 0 errors.
2. `python manage.py makemigrations --check --dry-run` reports no pending changes.
3. `python test/api_smoke.py` completes every step against a live server.
4. All manual test cases above pass, with the *Actual result* column filled in.
5. `npm run lint` and `npm run build` both succeed for the frontend.
