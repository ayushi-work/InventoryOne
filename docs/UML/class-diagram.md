# Class Diagram

The object-oriented model of the InventoryOne Broker Web App. Django models map
directly onto the classes below; the service objects on the right are plain
Python modules in `core/services/`.

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string first_name
        +bool is_staff
    }

    class Broker {
        +int id
        +User user
        +string phone
        +kyc_status
        +string pan_number
        +string aadhaar_number
        +string gst_number
        +string rera_number
        +string bank_account
        +string ifsc
        +bool agreement_accepted
        +upload_document()
        +accept_agreement()
    }

    class Project {
        +int id
        +string name
        +string code
        +string location
        +string status
        +text description
        +plots
        +availability_counts()
    }

    class Plot {
        +int id
        +Project project
        +string plot_number
        +decimal size_sq_yds
        +string facing
        +string status
        +decimal bsp
        +decimal plc_pct
        +decimal discount_pct
        +total_cost
        +reserve()
        +release()
        +mark_sold()
    }

    class Customer {
        +int id
        +Broker broker
        +string name
        +string email
        +string phone
        +text address
    }

    class Booking {
        +int id
        +Broker broker
        +Customer customer
        +Plot plot
        +decimal token_amount
        +string payment_mode
        +decimal commission_pct
        +string status
        +datetime created_at
        +datetime decided_at
        +approve()
        +reject()
    }

    class Commission {
        +int id
        +Booking booking
        +Broker broker
        +decimal amount
        +decimal tds_pct
        +decimal tds_amount
        +decimal net_amount
        +bool released
        +datetime released_at
        +release()
        +compute(plot)
    }

    class Document {
        +int id
        +Broker broker
        +Booking booking
        +string kind
        +string title
        +FileField file
        +int size_bytes
    }

    class Notification {
        +int id
        +Broker broker
        +string title
        +text body
        +string kind
        +string link
        +bool read
        +datetime created_at
        +mark_read()
    }

    class SupportTicket {
        +int id
        +Broker broker
        +string subject
        +text message
        +string status
        +string priority
        +text response
        +datetime resolved_at
    }

    class AuditLog {
        +int id
        +User actor
        +string action
        +string entity_type
        +string entity_id
        +json details
        +datetime created_at
    }

    class CompanyProfile {
        +int id
        +string name
        +string support_email
        +string support_phone
        +string rm_name
        +string rm_phone
        +string rm_email
    }

    class OTPCode {
        +int id
        +string email
        +string code
        +datetime expires_at
        +bool is_valid
        +generate_for()
    }

    class NotificationService {
        +notify(broker, title, body)
        +notify_brokers(brokers, title, body)
        +push_to_broker(broker, notification)
    }

    class DocumentService {
        +build_demand_letter_pdf(booking)
        +build_price_list_pdf(project)
        +build_kyc_summary_pdf(broker)
        +save_document(kind, content)
    }

    class AuditService {
        +log_action(actor, action, entity)
    }

    class InventoryConsumer {
        +connect()
        +disconnect()
        +broadcast_inventory()
    }

    User "1" o-- "0..1" Broker
    Broker "1" *-- "0..*" Customer
    Broker "1" *-- "0..*" Booking
    Broker "1" *-- "0..*" Commission
    Broker "1" *-- "0..*" Notification
    Broker "1" *-- "0..*" SupportTicket
    Broker "1" *-- "0..*" Document
    User "1" o-- "0..*" AuditLog

    Project "1" *-- "0..*" Plot
    Customer "1" -- "0..*" Booking
    Plot "1" -- "0..*" Booking
    Booking "1" o-- "0..1" Commission
    Booking "1" o-- "0..*" Document

    NotificationService ..> Notification
    DocumentService ..> Document
    AuditService ..> AuditLog
    InventoryConsumer ..> Plot
```

## Responsibility notes

| Class | Responsibility | Depends on |
| ----- | -------------- | ----------- |
| `Broker` | Broker identity, KYC state and agreement acceptance | `User` |
| `Plot` | Inventory state machine and pricing arithmetic | `Project` |
| `Booking` | Booking lifecycle (pending → approved / rejected) | `Broker`, `Customer`, `Plot` |
| `Commission` | Commission and TDS computation, release tracking | `Booking`, `Broker` |
| `Document` | File metadata for KYC uploads and generated PDFs | `Broker`, `Booking` |
| `Notification` | Per-broker message feed | `Broker` |
| `SupportTicket` | Broker support requests and company responses | `Broker` |
| `AuditLog` | Immutable traceability record | `User` |

The three service objects are stateless and depend only on the models, which keeps
them independently testable and avoids duplicating notification, PDF and audit logic
across the view layer.
