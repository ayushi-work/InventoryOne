# Entity Relationship Diagram

The InventoryOne data model centres on the **Plot**: every booking, document and
commission ultimately references a plot inside a project.

```mermaid
erDiagram
    USER ||--o| BROKER : "is"
    USER ||--o{ AUDIT_LOG : "performs"
    USER ||--o| COMPANY_PROFILE : "administers"

    BROKER ||--o{ CUSTOMER : "registers"
    BROKER ||--o{ BOOKING : "raises"
    BROKER ||--o{ COMMISSION : "earns"
    BROKER ||--o{ NOTIFICATION : "receives"
    BROKER ||--o{ SUPPORT_TICKET : "opens"
    BROKER ||--o{ DOCUMENT : "uploads"

    PROJECT ||--|{ PLOT : "contains"

    CUSTOMER ||--o{ BOOKING : "books"
    PLOT ||--o{ BOOKING : "is reserved by"

    BOOKING ||--o| COMMISSION : "generates"
    BOOKING ||--o{ DOCUMENT : "produces"

    USER {
        int id PK
        string username UK
        string email
        string first_name
        bool is_staff
    }

    BROKER {
        int id PK
        int user_id FK
        string phone
        string kyc_status "pending|approved|rejected"
        string pan_number
        string aadhaar_number
        string gst_number
        string rera_number
        string bank_account
        string ifsc
        bool agreement_accepted
        datetime created_at
    }

    PROJECT {
        int id PK
        string name
        string code UK
        string location
        string status "active|upcoming|closed"
        text description
    }

    PLOT {
        int id PK
        int project_id FK
        string plot_number
        decimal size_sq_yds
        string facing
        string status "available|on_hold|sold"
        decimal bsp
        decimal plc_pct
        decimal discount_pct
    }

    CUSTOMER {
        int id PK
        int broker_id FK
        string name
        string email
        string phone
        text address
    }

    BOOKING {
        int id PK
        int broker_id FK
        int customer_id FK
        int plot_id FK
        decimal token_amount
        string payment_mode
        decimal commission_pct
        string status "pending|approved|rejected"
        datetime created_at
        datetime decided_at
    }

    COMMISSION {
        int id PK
        int booking_id FK
        int broker_id FK
        decimal amount
        decimal tds_pct
        decimal tds_amount
        decimal net_amount
        bool released
        datetime released_at
    }

    DOCUMENT {
        int id PK
        int broker_id FK
        int booking_id FK
        string kind
        string title
        string file
        int size_bytes
    }

    NOTIFICATION {
        int id PK
        int broker_id FK
        string title
        text body
        string kind
        string link
        bool read
        datetime created_at
    }

    SUPPORT_TICKET {
        int id PK
        int broker_id FK
        string subject
        text message
        string status "open|in_progress|resolved"
        string priority
        text response
    }

    AUDIT_LOG {
        int id PK
        int actor_id FK
        string action
        string entity_type
        string entity_id
        json details
        datetime created_at
    }

    COMPANY_PROFILE {
        int id PK
        string name
        string support_email
        string rm_name
        string rm_phone
        string rm_email
    }
```

## Cardinality notes

- A **User** has at most one **Broker** profile; administrators are `User` rows with
  `is_staff = true` and no broker profile.
- A **Project** owns many **Plots**. A plot number is unique *within* a project
  (`uniq_plot_per_project`).
- A **Plot** may appear in many **Bookings** over time, but at most one booking may be
  `pending` at a time (`uniq_open_booking_per_plot`). Historical bookings stay for audit.
- A **Booking** produces at most one **Commission**, created only when the administrator
  approves it.
- **Documents** attach either to a broker (KYC uploads, price lists) or to a booking
  (generated demand letters).
- Every **AuditLog** entry records an action against an entity so approvals and
  commission releases stay traceable (SRS NFR-10).
