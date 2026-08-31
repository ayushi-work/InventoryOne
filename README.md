# InventoryOne — Broker Web App

## Project Description

The **InventoryOne — Broker Web App** is a real-estate platform that allows registered brokers to register and log in via OTP with KYC verification, view active projects with live colour-coded plot availability, view plot details, register customers, raise booking requests, track commissions, download documents, and stay updated via notifications.

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
