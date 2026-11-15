# InventoryOne: Broker Web App

## Project Description

The **InventoryOne: Broker Web App** is a real-estate platform that allows registered brokers to register and log in via OTP with KYC verification, view active projects with live colour-coded plot availability, view plot details, register customers, raise booking requests, track commissions, download documents, and stay updated via notifications.

Company administrators can manage projects, plot inventory, and broker bookings, and approve or reject booking requests.

The project will be developed using the **Agile methodology**, with development divided into short sprints for continuous development, testing, and improvement.

---

## Team Members

| Member           | Role               | Responsibilities                                                     |
| ---------------- | ------------------ | -------------------------------------------------------------------- |
| **Avni**         | TBD | TBD |
| **Ayushi**       | TBD       | TBD                     |

---

## Technologies

| Layer              | Technology                           |
| ------------------ | ------------------------------------ |
| Frontend           | Next.js + TypeScript                 |
| Backend            | Django + Django REST Framework       |
| Database           | PostgreSQL                           |
| ORM                | Django ORM                           |
| Real-time          | Django Channels + Redis              |
| Authentication     | Firebase Auth / Django authentication |
| File storage       | AWS S3                               |
| Notifications      | Firebase Cloud Messaging             |
| Maps               | Google Maps API                      |
| Payments           | TBD                                  |
| Background jobs    | Celery + Redis                       |
| Admin              | Django Admin                         |
| Deployment         | AWS / Render / Railway               |
| CI/CD              | GitHub Actions                       |

---

## Project Structure

```text
InventoryOne/
│
├── README.md
│
├── docs/
│   ├── SRS/
│   └── UML/
│
├── src/
│   ├── frontend/
│   └── backend/
│
├── test/
│
└── .gitignore
```

| Directory       | Purpose                             |
| --------------- | ----------------------------------- |
| `docs/SRS/`     | Software Requirements Specification |
| `docs/UML/`     | UML and system design diagrams      |
| `src/frontend/` | Frontend source code                |
| `src/backend/`  | Backend source code and APIs        |
| `test/`         | Test cases and testing code         |
| `.gitignore`    | Files excluded from version control |

### Documentation Index

| Document                       | Experiment | Contents                                    |
| ------------------------------ | ---------- | ------------------------------------------- |
| `docs/feasibility-analysis.md` | 2          | Problem identification and feasibility     |
| `docs/SRS/srs.md`              | 4          | Software Requirements Specification        |
| `docs/UML/use-case.md`         | 5          | Use case diagram and use case narratives    |
| `docs/design-analysis.md`      | 8          | Software design principles analysis        |
| `docs/UML/er-diagram.md`       | —          | Entity relationship diagram                 |
| `docs/UML/class-diagram.md`    | —          | Class diagram                              |
| `docs/UML/sequence-diagram.md` | —          | Sequence diagrams for the core workflows   |
| `docs/UML/activity-diagram.md` | —          | Activity diagrams                          |
| `docs/presentation/`           | —          | Student presentation deck (PPTX + Markdown) |
| `test/test-cases.md`           | —          | Manual test cases and exit criteria        |
| `test/api_smoke.py`            | —          | End-to-end API smoke test                  |

---

# Running the Application

## Prerequisites

- Python 3.11 – 3.13
- Node.js 20+
- PostgreSQL 14+

## 1. Backend (Django + DRF)

```bash
cd src/backend

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create the database (once)
createdb inventoryone

# Apply migrations and load demo data
python manage.py migrate
python manage.py seed_demo

# Start the API on http://127.0.0.1:8000
# Daphne serves both HTTP and the live-inventory WebSocket
python -m daphne -b 127.0.0.1 -p 8000 inventoryone.asgi:application
```

Optional services (the app degrades gracefully without them):

```bash
# Redis - powers live inventory updates and Celery background jobs
redis-server

# Celery worker - demand letters and notification fan-out
celery -A inventoryone worker -l info
```

## 2. Frontend (Next.js)

```bash
cd src/frontend

npm install
npm run dev      # http://127.0.0.1:3000
```

The frontend talks to the API at `http://127.0.0.1:8000` by default. Override it with
`NEXT_PUBLIC_API_URL` (and `NEXT_PUBLIC_WS_URL` for the WebSocket) if the API runs
elsewhere.

## 3. Docker (full stack)

```bash
cp .env.example .env   # then fill in the values
docker compose up --build
```

Brings up PostgreSQL, Redis, the Django/Daphne backend, a Celery worker and the
Next.js frontend.

## Demo Logins

| Role                   | Email                     | Notes                                |
| ---------------------- | ------------------------- | ------------------------------------ |
| Broker                 | `broker@example.com`      | Sign in with OTP (dev code is shown) |
| Broker (KYC pending)   | `priya.broker@example.com`| Sign in with OTP                     |
| Company Administrator  | `admin@inventoryone.local`| Sign in with OTP; Django Admin password `admin123` |

In development the OTP is returned directly by `POST /api/auth/request-otp/` because e-mail
delivery is stubbed. Set `OTP_DEBUG_MODE = False` in `src/backend/.env` for production.

## 4. Tests

```bash
# Unit + API test suite (33 tests)
cd src/backend && python manage.py test core

# End-to-end smoke test against a running server (41 checks)
python test/api_smoke.py

# Frontend
cd src/frontend && npm run lint && npm run build
```

## Feature Overview

| Area | What it does |
| ---- | ------------ |
| Authentication | OTP-based registration and login, token auth, rate limiting |
| KYC | PAN / Aadhaar / GST / cancelled cheque uploads (S3 or local disk), bank details, approval workflow |
| Projects & inventory | Live colour-coded availability, plot CRUD, bulk plot grid creation, Google Maps embed |
| Customers | CRM-style registration linked to the broker |
| Bookings | Token amount + payment mode, row-locked double-booking prevention, approval/rejection |
| Commission | 2 % of plot cost, 10 % TDS, net payable, release workflow |
| Documents | Price lists, demand letters and KYC summaries generated as PDFs |
| Notifications | In-app feed plus Firebase Cloud Messaging push, bell badge with unread count |
| Support | Ticket raising, relationship manager contact, admin response and resolution |
| Live updates | Django Channels over Redis pushes plot changes to every open dashboard |
| Audit trail | Every approval, release and inventory change is recorded with an actor and timestamp |
| Administration | Dashboard statistics, project/plot management, KYC approval, broadcasts, ticket queue |

## API Overview

| Method | Endpoint                             | Purpose                              |
| ------ | ------------------------------------ | ------------------------------------ |
| GET    | `/api/health/`                       | Liveness / readiness probe           |
| POST   | `/api/auth/request-otp/`             | Send an OTP to an e-mail             |
| POST   | `/api/auth/verify-otp/`              | Verify OTP and receive an auth token |
| GET    | `/api/me/`                           | Broker profile and KYC status         |
| PATCH  | `/api/me/`                           | Update KYC and bank details          |
| GET    | `/api/kyc/summary/`                  | Download the KYC summary PDF         |
| GET    | `/api/projects/`                     | Active projects with availability    |
| GET    | `/api/projects/<id>/`                | Project detail with plot inventory   |
| GET    | `/api/customers/`                    | Customers registered by the broker   |
| POST   | `/api/customers/`                    | Register a customer                  |
| GET    | `/api/bookings/`                     | Bookings raised by the broker        |
| POST   | `/api/bookings/`                     | Raise a booking request              |
| GET    | `/api/commissions/`                  | Commission ledger for the broker     |
| GET    | `/api/documents/`                    | KYC files and downloads              |
| POST   | `/api/documents/`                    | Upload a KYC document                |
| GET    | `/api/documents/<id>/download/`      | Download a stored document           |
| POST   | `/api/projects/<id>/price-list/`     | Generate the price list PDF          |
| POST   | `/api/bookings/<id>/demand-letter/`  | Generate the demand letter PDF       |
| GET    | `/api/notifications/`                | Notification feed                    |
| GET    | `/api/notifications/unread-count/`   | Unread badge count                   |
| POST   | `/api/notifications/mark-read/`      | Mark notifications as read           |
| GET    | `/api/tickets/`                      | Broker support tickets               |
| POST   | `/api/tickets/`                      | Raise a support ticket               |
| GET    | `/api/company/`                      | Company and relationship manager details |
| GET    | `/api/admin/stats/`                  | Company dashboard statistics         |
| GET    | `/api/admin/projects/`               | All projects                         |
| POST   | `/api/admin/projects/`               | Create a project                     |
| GET    | `/api/admin/projects/<id>/plots/`    | Plot inventory of a project          |
| POST   | `/api/admin/projects/<id>/plots/`    | Bulk-create plots                    |
| PUT    | `/api/admin/plots/<id>/`             | Update a plot                        |
| GET    | `/api/admin/bookings/`               | All booking requests                 |
| POST   | `/api/admin/bookings/<id>/decide/`   | Approve or reject a booking          |
| GET    | `/api/admin/commissions/`            | All commissions                      |
| POST   | `/api/admin/commissions/<id>/release/` | Release a commission              |
| GET    | `/api/admin/tickets/`                | Support ticket queue                 |
| GET    | `/api/admin/brokers/`                | All brokers                          |
| POST   | `/api/admin/brokers/`                | Approve or reject KYC                |
| POST   | `/api/admin/broadcast/`              | Notify every broker                  |
| GET    | `/api/admin/audit-log/`              | Traceability records                 |

---

# Software Engineering Tools

| Activity                   | Tool                  |
| -------------------------- | --------------------- |
| Requirements Documentation | Google Docs / MS Word |
| UML Design                 | Draw.io               |
| Programming                | VS Code               |
| Version Control            | Git                   |
| Code Repository            | GitHub                |
| Project Management         | GitHub Projects       |
| API Testing                | Postman               |
| Database                   | PostgreSQL            |
| Testing                    | PyTest / JUnit        |
| Documentation              | Markdown              |

---

# Agile Methodology

The project follows the **Agile Software Development methodology**. Development is divided into short **sprints**, with each sprint delivering a specific set of features.

### Agile Workflow

```text
Product Backlog
      ↓
Sprint Planning
      ↓
Development
      ↓
Testing
      ↓
Sprint Review
      ↓
Retrospective
      ↓
Next Sprint
```

### Sprint Plan

| Sprint       | Focus                                        |
| ------------ | -------------------------------------------- |
| **Sprint 1** | Requirements, SRS, UML, and GitHub setup     |
| **Sprint 2** | Database, broker login, and profile/KYC      |
| **Sprint 3** | Projects and plot inventory with live availability |
| **Sprint 4** | Customer registration and booking requests  |
| **Sprint 5** | Commission module and documents              |
| **Sprint 6** | Notifications, support, integration, testing, and final improvements |

---

# Experiment 1: Introduction to Software Engineering Tools and Project Setup

## Aim

To select a real-world software project, form a development team, create a GitHub repository, establish the initial project structure, and demonstrate basic Git version-control operations.

## Objectives

* Select a real-world software project.
* Define team roles and responsibilities.
* Create a GitHub repository.
* Establish the initial project structure.
* Understand basic Git operations.
* Set up the project for collaborative development using GitHub.
* Plan development using Agile sprints.

---

# Problem Statement

Traditional real-estate plot booking relies on manual coordination between brokers and the company, making it difficult for brokers to see live inventory, track bookings, and manage their commissions.

The proposed **InventoryOne — Broker Web App** provides a digital platform where each broker can log in with OTP verification, complete KYC, view active projects with live colour-coded plot availability, register customers, and raise booking requests directly.

The system should allow the company administrator to approve or reject bookings and manage commissions, while brokers can track payments, download documents, and stay updated through notifications.

---

# Selected Project

**Project Title:** InventoryOne — Broker Web App

**Domain:** Real Estate / Property Management

**Development Methodology:** Agile

## Main Users

### Broker

* Register and log in via OTP
* Complete KYC verification (PAN, Aadhaar, GST, cancelled cheque, RERA number, bank details)
* View active projects
* View live plot availability with colour coding
* View plot details (size, facing, PLC, BSP, total cost, discount)
* Register customers
* Raise booking requests
* Track commissions
* Download documents
* Receive notifications
* Raise support tickets

### Company Administrator

* Manage projects
* Manage plot inventory
* Approve or reject booking requests
* Manage commissions and releases
* Generate demand letters

---

# Project Setup

Create the project structure in VS Code:

```text
InventoryOne/
│
├── README.md
├── docs/
│   ├── SRS/
│   └── UML/
├── src/
│   ├── frontend/
│   └── backend/
├── test/
└── .gitignore
```

---

# GitHub Repository Setup

1. Sign in to GitHub.
2. Create a new repository named `InventoryOne`.
3. Add the project `README.md`.
4. Select the required repository visibility.
5. Add **Avni** and **Ayushi** as collaborators.
6. Clone the repository locally.
7. Open the project in VS Code.
8. Create the initial project structure.
9. Commit and push the changes.

---

# Basic Git Commands

| Operation             | Command                                  |
| --------------------- | ---------------------------------------- |
| Check Git version     | `git --version`                          |
| Initialize repository | `git init`                               |
| Check status          | `git status`                             |
| Add files             | `git add .`                              |
| Commit changes        | `git commit -m "Initial project setup"`  |
| Add remote            | `git remote add origin <repository-url>` |
| Set main branch       | `git branch -M main`                     |
| Push changes          | `git push -u origin main`                |
| Pull changes          | `git pull origin main`                   |
| View history          | `git log --oneline`                      |
| Clone repository      | `git clone <repository-url>`             |

---

# Version Control Demonstration

### Step 1: Initialize the Repository

```bash
git init
```

### Step 2: Check Repository Status

```bash
git status
```

### Step 3: Stage Project Files

```bash
git add .
```

### Step 4: Create the Initial Commit

```bash
git commit -m "Initial project setup"
```

### Step 5: Connect to GitHub

```bash
git remote add origin <repository-url>
```

### Step 6: Push the Project

```bash
git branch -M main
git push -u origin main
```

### Step 7: Commit a Change

After modifying the project:

```bash
git add .
git commit -m "Update project documentation"
```

### Step 8: Push Changes

```bash
git push
```

### Step 9: View Commit History

```bash
git log --oneline
```

### Step 10: Get Changes from Team Members

```bash
git pull origin main
```

---

# Collaborative Development

The team will use GitHub to collaborate on different features.

Feature branches can be created for individual tasks:

```text
main
│
├── feature/broker-auth
├── feature/projects-inventory
├── feature/customers-bookings
├── feature/commissions
└── feature/notifications-support
```

Example:

```bash
git pull origin main
git switch -c feature/projects-inventory
```

After completing the feature:

```bash
git add .
git commit -m "Add projects and inventory"
git push -u origin feature/projects-inventory
```

A **Pull Request** can then be created on GitHub for review before merging the feature into `main`.

---

# Product Backlog

| ID   | User Story                                                  | Priority |
| ---- | ----------------------------------------------------------- | -------- |
| US01 | As a broker, I want to register and log in using OTP so that I can access the platform. | High |
| US02 | As a broker, I want to complete KYC verification so that my profile is approved. | High |
| US03 | As a broker, I want to view active projects so that I can find available inventory. | High |
| US04 | As a broker, I want to view live plot availability with colour coding so that I can see which plots are available, booked, or on hold. | High |
| US05 | As a broker, I want to view plot details such as size, facing, and pricing. | Medium |
| US06 | As a broker, I want to register customers so that bookings can be linked to them. | High |
| US07 | As a broker, I want to raise booking requests with token amount and payment mode. | High |
| US08 | As an administrator, I want to approve or reject booking requests. | High |
| US09 | As a broker, I want to track my commissions and payments. | High |
| US10 | As a broker, I want to download documents such as price lists and forms. | Medium |
| US11 | As a broker, I want to receive notifications for new projects, schemes, and booking updates. | Medium |
| US12 | As a broker, I want to raise support tickets and contact my relationship manager. | Medium |

---

# Functional Requirements

The system should provide:

* OTP-based broker login and registration
* KYC upload (PAN, Aadhaar, GST, cancelled cheque)
* RERA registration and bank details
* Broker profile status and agreement acceptance
* Active project listing with project details
* Live plot availability with colour coding
* Plot details with pricing and discounts
* Customer registration (CRM integration)
* Booking requests with company approval
* Commission tracking with TDS
* Document downloads
* Notifications
* Support tickets

---

# Non-Functional Requirements

* **Usability:** The system should be simple and easy to use.
* **Performance:** Project and inventory operations should respond quickly.
* **Security:** Unauthorized users should not be able to access administrative functions.
* **Reliability:** Booking and commission data should be stored correctly without data loss.
* **Scalability:** The system should support additional projects, plots, and brokers.
* **Maintainability:** The source code should be modular and documented.
* **Responsiveness:** The broker interface should work properly on desktop and mobile browsers.

---

# System Workflow

```text
Broker
   ↓
OTP Login
   ↓
Browse Active Projects
   ↓
View Live Plot Availability
   ↓
Register Customer
   ↓
Raise Booking Request
   ↓
Company Approval
   ↓
Commission Tracking
   ↓
Notifications & Documents
   ↓
Broker
```

---

# Testing Strategy

Testing will be performed throughout the Agile development process.

The project will use:

* Unit Testing
* Integration Testing
* Functional Testing
* API Testing
* System Testing
* User Acceptance Testing
* Regression Testing

Testing tools may include **PyTest/JUnit** and **Postman**.

---

# Documentation

Project documentation will be maintained in the `docs/` directory.

```text
docs/
│
├── SRS/
│   └── Software Requirements Specification
│
└── UML/
    ├── Use Case Diagram
    ├── Class Diagram
    ├── Sequence Diagram
    ├── Activity Diagram
    └── ER Diagram
```

---

# Expected Outcome

The GitHub repository should contain the initial **InventoryOne — Broker Web App** structure, documentation, source-code directories, testing directory, and Git history.

The two-member team should be able to collaborate effectively using GitHub while following the Agile development process.

---

# Observation

Git and GitHub provide effective version control and collaboration, while Agile enables the project to be developed incrementally through short sprints.

The initial repository and project structure provide a foundation for requirements analysis, design, implementation, testing, and future deployment.

---

# Result

An **InventoryOne — Broker Web App** was selected as the real-world software project. The project team was formed, a GitHub repository was created, and the initial project structure was established.

Basic Git operations including **status, add, commit, push, pull, and log** were demonstrated. The project was organized using the **Agile methodology** to support incremental development, collaboration, and continuous testing.
