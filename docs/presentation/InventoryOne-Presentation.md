---
marp: true
theme: default
paginate: true
size: 16:9
header: 'InventoryOne — Broker Web App'
footer: 'SE & DP Lab · Student Presentation'
style: |
  section {
    font-family: 'Segoe UI', Calibri, Arial, sans-serif;
    color: #222;
    background: #ffffff;
    font-size: 26px;
    padding: 50px 55px;
  }
  h1 { color: #1F3864; font-size: 50px; margin-bottom: 8px; }
  h2 { color: #1F3864; font-size: 34px; border-bottom: 3px solid #2E9E8F; padding-bottom: 6px; }
  h3 { color: #2E9E8F; margin: 6px 0; }
  strong { color: #1F3864; }
  ul { margin: 4px 0; }
  li { margin: 3px 0; font-size: 0.82em; }
  table { font-size: 0.72em; border-collapse: collapse; width: 100%; }
  th { background: #1F3864; color: #fff; padding: 6px 8px; }
  td { border: 1px solid #D5DCE8; padding: 5px 8px; }
  section.lead { background: #1F3864; color: #fff; }
  section.lead h1 { color: #fff; }
  section.lead h2 { color: #2E9E8F; border: none; }
  .cols { display: flex; gap: 22px; }
  .col { flex: 1; background: #F2F4F8; border-radius: 8px; padding: 14px 16px; }
  .green { border-top: 5px solid #2E7D32; }
  .teal  { border-top: 5px solid #2E9E8F; }
  .amber { border-top: 5px solid #F29E1B; }
  .red   { border-top: 5px solid #C0392B; }
  .navy  { border-top: 5px solid #1F3864; }
  .pill { display:inline-block; padding:3px 12px; border-radius:14px; font-size:0.6em; font-weight:bold; color:#fff; }
  .p-green{background:#2E7D32;} .p-amber{background:#F29E1B;} .p-red{background:#C0392B;}
---

<!-- _class: lead -->
<!-- _paginate: false -->

# InventoryOne
### Broker Web App — Real-Estate Plot Booking Platform

**Selected Software System:** A digital platform where registered brokers view live plot inventory, register customers, raise booking requests, track commissions and receive notifications.

**Group Members:** Avni · Ayushi  
**Domain:** Real Estate / Property Management · **Methodology:** Agile

---

## 2. Introduction, Problem Statement & Objectives

<div class="cols">
<div class="col teal">

### Introduction
- Real-estate plot booking today relies on manual coordination between brokers and the company.
- Brokers must call/visit the office to check availability, raise bookings and track earnings.
- **InventoryOne** is a self-service web app giving brokers live plot visibility and digital bookings.
- Administrators manage projects, inventory, approvals and commissions from one dashboard.

</div>
<div class="col red">

### Problem Statement
- Stale inventory data and no live visibility of plot availability.
- Slow, error-prone booking through phone/email and spreadsheets.
- No transparent commission tracking for brokers.
- Limited service hours and heavy manual coordination.

</div>
<div class="col green">

### Objectives
- Secure OTP-based broker login and KYC verification.
- Live, colour-coded plot availability.
- Customer registration and booking with approval.
- Automated commission, TDS and documents.
- Real-time notifications and support tickets.

</div>
</div>

---

## 3. Major Functional & Non-Functional Requirements

<div class="cols">
<div class="col navy" style="flex:1.7">

### Functional Requirements
- OTP-based broker registration, login and session expiry.
- KYC upload (PAN, Aadhaar, GST, cancelled cheque) + RERA & bank details.
- Active project listing with project details.
- Live colour-coded plot availability: <span class="pill p-green">available</span> <span class="pill p-amber">on hold</span> <span class="pill p-red">sold</span>
- Plot details: size, facing, PLC, BSP, total cost, discount.
- Customer registration linked to the broker.
- Booking requests with token amount and payment mode.
- Administrator approval / rejection of bookings.
- Commission tracking with TDS and net payable; document downloads.
- Notifications and support tickets.

</div>
<div class="col teal">

### Non-Functional Requirements
- **Usability:** simple, minimal training.
- **Performance:** operations respond < 2 s.
- **Security:** role-based access; HTTPS; protected OTP/KYC.
- **Reliability:** no loss of booking/commission data.
- **Scalability:** supports more projects, plots, brokers.
- **Maintainability:** modular and documented.
- **Responsiveness:** desktop and mobile.

</div>
</div>

---

## 4. Actors & UML Use Case Diagram

```mermaid
flowchart LR
    Broker(("Broker"))
    Admin(("Company\nAdministrator"))

    subgraph SYS["InventoryOne — Broker Web App"]
        UC1([Register / OTP Login])
        UC2([Complete KYC])
        UC3([View Plot Availability])
        UC4([Register Customer])
        UC5([Raise Booking Request])
        UC6([Track Commission])
        UC7([Approve / Reject Booking])
        UC8([Manage Projects & Inventory])
        UC9([Manage Commissions])
    end

    Broker --- UC1
    Broker --- UC2
    Broker --- UC3
    Broker --- UC4
    Broker --- UC5
    Broker --- UC6
    Admin --- UC7
    Admin --- UC8
    Admin --- UC9
```

**Actors:** Broker (primary) · Company Administrator (secondary)  
**External systems:** OTP/SMS Gateway, AWS S3, Firebase FCM, Google Maps  
**Relationships:** `<<include>>` Authenticate Broker & Validate KYC · `<<extend>>` Upload KYC Documents

---

## 5. Data Flow Diagram — DFD Level 0 (Context)

```mermaid
flowchart LR
    Broker[Broker] -->|credentials, KYC, booking request| S((0\nInventoryOne\nBroker Web App))
    S -->|availability, status, commissions| Broker
    Admin[Company Administrator] -->|approve / reject, manage| S
    S -->|pending bookings, reports| Admin
    OTP[OTP / SMS Gateway] --- S
    S -->|push notifications| FCM[Firebase Cloud Messaging]
    S --- S3[AWS S3]
```

**Level 1 processes:** 1.0 Authentication · 2.0 KYC · 3.0 Project & Inventory · 4.0 Customer & Booking · 5.0 Commission · 6.0 Notification  
**Data stores:** D1 Brokers · D2 Projects/Plots · D3 Customers · D4 Bookings · D5 Commissions

---

## 6. Software Architecture & Major Modules

<div class="cols">
<div class="col" style="flex:2">

**Presentation Layer** — Next.js + TypeScript · Broker & Admin web UI (responsive)

**API Layer** — Django REST Framework · OTP / Token auth · REST endpoints

**Business / Application Modules** — Auth · KYC · Project & Inventory · Customer · Booking · Commission · Notification · Support · Admin

**Data & External Services** — PostgreSQL · Redis · AWS S3 · Firebase FCM · Google Maps · OTP/SMS Gateway

</div>
<div class="col teal">

### Major Modules
- Authentication (OTP)
- KYC Verification
- Project & Inventory
- Customer Management
- Booking & Approval
- Commission & TDS
- Notification
- Documents
- Support Tickets
- Admin & Reports

</div>
</div>

---

## 7. Module Cohesion, Coupling & Design Considerations

<div class="cols">
<div class="col green">

### Cohesion — High / Functional
- Each module performs exactly one responsibility.
- Auth → only identity verification.
- KYC → only document handling.
- Commission → only commission & TDS.
- Notification → only message delivery.
- *Benefit:* easier testing, reuse, maintenance.

</div>
<div class="col teal">

### Coupling — Low
- Modules communicate via clean interfaces.
- Auth ↔ OTP gateway → **message** coupling.
- Booking ↔ Inventory → **data** coupling.
- Admin → Booking → **control** coupling.
- *Benefit:* changes stay localised.

</div>
<div class="col amber">

### Design Considerations
- Modularization & information hiding.
- Abstraction hides implementation.
- **SOLID:** SRP, OCP, LSP, ISP, DIP.
- OO model: Broker, Project, Plot, Customer, Booking, Commission.
- Top-down decomposition + bottom-up integration.

</div>
</div>

---

## 8. SDLC Model — Agile

```mermaid
flowchart LR
    A[Product Backlog] --> B[Sprint Planning] --> C[Development] --> D[Testing] --> E[Sprint Review] --> F[Retrospective]
    F -.->|next sprint| A
```

### Justification
- Requirements **evolve** — Agile supports change through short sprints.
- Delivers **working increments** early (auth → inventory → booking → commission).
- Continuous testing and broker feedback improve quality.
- Two-member team suits short, focused iterations.
- **Sprint plan (1–6):** setup → DB/login/KYC → inventory → booking → commission → notifications.
- Git feature branches + pull requests enable collaboration.

---

## 9. Major Challenges, Security Concerns & Improvements

<div class="cols">
<div class="col red">

### Major Challenges
- Ensuring real-time availability accuracy.
- Preventing double booking of a plot.
- Handling KYC uploads and validation.
- Integrating multiple third-party services.
- Accurate commission and TDS computation.

</div>
<div class="col navy">

### Security Concerns
- OTP reuse / brute-force attempts.
- Protecting sensitive KYC & bank data.
- Role-based access for admin functions.
- Secure document storage (S3, encryption).
- HTTPS everywhere; no secrets in logs.

</div>
<div class="col green">

### Possible Improvements
- Integrated payment gateway & digital demand letters.
- QR-based booking and biometric login.
- Analytics dashboard for sales & inventory.
- Offline / PWA support and native mobile app.
- AI-based lead & price recommendations.

</div>
</div>

---

## 10. Key Learnings & Conclusion

<div class="cols">
<div class="col navy">

### Key Learnings
- Applied the full SDLC: requirements → design → implementation.
- Wrote a structured SRS traced to user stories.
- Modelled actors, use cases and data flows.
- Understood modularity, high cohesion, low coupling.
- Practised Agile sprints and Git/GitHub collaboration.
- Learned secure design for sensitive broker/KYC data.

</div>
<div class="col teal">

### Conclusion
- InventoryOne digitises real-estate plot booking for brokers.
- Provides live inventory, digital bookings and transparent commissions.
- A modular, secure, scalable and maintainable web application.
- Built iteratively with Agile, enabling continuous improvement.
- Foundation ready for payments, analytics and mobile expansion.

</div>
</div>

<!-- _paginate: false -->
### Thank You
