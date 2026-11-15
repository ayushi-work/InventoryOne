# Sequence Diagrams

## 1. Broker login with OTP

```mermaid
sequenceDiagram
    actor Broker
    participant UI as Login Page
    participant API as Django REST API
    participant OTPCode as OTPCode model
    participant Token as Auth Token

    Broker->>UI: Enter e-mail address
    UI->>API: POST /api/auth/request-otp/
    API->>API: Get or create User + Broker profile
    API->>OTPCode: generate_for(email) (6-digit, 5-min expiry)
    API-->>UI: 200 OK { dev_code (debug only) }
    UI-->>Broker: OTP delivered (echoed in development)

    Broker->>UI: Enter OTP
    UI->>API: POST /api/auth/verify-otp/
    API->>OTPCode: lookup(email, code), check expiry
    alt invalid or expired
        OTPCode-->>API: no match
        API-->>UI: 400 Bad Request
    else valid
        OTPCode-->>API: match
        API->>OTPCode: delete (single use)
        API->>Token: get_or_create(user)
        API-->>UI: 200 OK { token, role, broker }
        UI->>UI: store session in localStorage
        UI-->>Broker: Redirect to dashboard
    end
```

## 2. Raise a booking request

```mermaid
sequenceDiagram
    actor Broker
    participant UI as Project Detail
    participant API as Django REST API
    participant DB as PostgreSQL
    participant WS as Channels (Redis)

    Broker->>UI: Select an available plot
    UI->>API: GET /api/projects/<id>/
    API->>DB: Query project + plots
    API-->>UI: 200 OK { plots with status }
    UI-->>Broker: Colour-coded plot grid

    Broker->>UI: Click plot, fill token amount + payment mode
    UI->>API: POST /api/bookings/
    API->>DB: BEGIN; SELECT ... FOR UPDATE plot
    alt plot not available
        API->>DB: ROLLBACK
        API-->>UI: 409 Conflict
    else available
        API->>DB: INSERT booking (pending)
        API->>DB: UPDATE plot status = on_hold
        API->>DB: COMMIT
        API->>WS: broadcast inventory update
        API-->>UI: 201 Created { booking }
        UI-->>Broker: "Booking request raised"
    end
```

## 3. Administrator approves a booking

```mermaid
sequenceDiagram
    actor Admin
    participant UI as Admin Console
    participant API as Django REST API
    participant DB as PostgreSQL
    participant Task as Celery Task
    participant WS as Channels (Redis)
    participant Notify as Notification Service

    Admin->>UI: Open pending bookings
    UI->>API: GET /api/admin/bookings/?status=pending
    API->>DB: Query bookings + customer + plot
    API-->>UI: 200 OK [ bookings ]

    Admin->>UI: Click Approve
    UI->>API: POST /api/admin/bookings/<id>/decide/ { action: approve }
    API->>DB: UPDATE booking status = approved
    API->>DB: UPDATE plot status = sold
    API->>DB: INSERT commission (gross, 10% TDS, net)
    API->>DB: INSERT audit_log (booking.approved)
    API->>Notify: notify(broker, "Booking approved")
    API->>Task: generate_demand_letter_task.delay(booking_id)
    Task->>DB: INSERT demand letter document
    API->>WS: broadcast inventory update
    API-->>UI: 200 OK { booking, commission }
    UI-->>Admin: "Approved - plot marked sold, commission created"
```

## 4. Live inventory update

```mermaid
sequenceDiagram
    participant Dash as Broker Dashboard
    participant WS as WebSocket /ws/inventory/
    participant API as Django REST API
    participant DB as PostgreSQL
    participant Redis as Redis (channel layer)

    Dash->>WS: connect
    WS->>Redis: group_add('inventory')
    WS-->>Dash: { type: connected }

    Admin->>API: approve a booking (plot -> sold)
    API->>DB: UPDATE plot status
    API->>Redis: group_send('inventory', inventory_update)
    Redis-->>WS: deliver message
    WS-->>Dash: { type: inventory, plot_id, status, counts }
    Dash->>API: GET /api/projects/<id>/
    API-->>Dash: fresh plot list
    Dash-->>Admin: plot tile turns red without a page reload

    Note over Dash: If the socket cannot open the client falls back to 15-second polling
```
