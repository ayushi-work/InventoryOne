# Experiment 8: Software Design Principles

## Aim

To analyse the **InventoryOne: Broker Web App** using fundamental software design principles and prepare a detailed design analysis report by applying modularization, abstraction, information hiding, coupling, cohesion, function-oriented design, object-oriented design, and top-down/bottom-up design approaches.

## Objectives

- Understand the importance of software design in the Software Development Life Cycle.
- Study major software design principles and quality attributes.
- Identify the logical modules of the InventoryOne Broker Web App.
- Evaluate the InventoryOne design based on coupling and cohesion.
- Compare function-oriented and object-oriented approaches.
- Prepare a comprehensive design analysis report.

## Introduction

Software design is the bridge between software requirements and implementation. After completing the Software Requirement Specification (SRS), developers transform user requirements into a structured technical solution. A good design simplifies implementation, improves maintainability, reduces development cost and facilitates future enhancements. The design phase determines the architecture, modules, interfaces, data structures and interactions among system components.

---

# Conceptual Background

## Characteristics of Good Software Design

A good software design should be modular, reusable, scalable, secure, efficient, reliable, maintainable and easy to test. It should minimise complexity while maximising readability and extensibility.

## Modularization

Modularization divides a large software system into smaller independent modules. Each module performs a single well-defined responsibility. For the InventoryOne Broker Web App, Authentication, KYC, Project & Inventory, Customer, Booking, Commission, Notification, Document and Support are separate modules.

## Abstraction

Abstraction focuses on essential behaviour while hiding implementation details. A broker interacts only with services such as *View Live Plot Availability* or *Raise Booking Request* without knowing how inventory status, database persistence or notification delivery are internally executed.

## Information Hiding

Each module hides its internal implementation and exposes only necessary interfaces. For example, the OTP generation and verification logic is hidden inside the Authentication module, and commission/TDS calculation is hidden inside the Commission module.

## Coupling

Coupling measures interdependence between modules. Low coupling is desirable because changes in one module should have minimal impact on others.

## Cohesion

Cohesion measures how closely related the responsibilities of a module are. Functional cohesion, where a module performs exactly one task, is considered the highest quality.

## Function-Oriented Design

The software is decomposed into functions. Data flows between functions and each function performs a specific operation.

## Object-Oriented Design

The system is modelled using classes and objects that encapsulate data and behaviour. In the InventoryOne Broker Web App, classes such as `Broker`, `Project`, `Plot`, `Customer`, `Booking` and `Commission` collaborate through object interactions.

## Top-Down Design

Development begins with the overall system and progressively decomposes it into smaller modules.

## Bottom-Up Design

Low-level reusable components are developed first and then integrated into higher-level subsystems.

---

# Problem Statement

Analyse the InventoryOne Broker Web App using software design principles and prepare a design analysis report highlighting modularization, coupling, cohesion and design approaches.

---

# Solved Example: InventoryOne Broker Web App

## Step 1: Identify Functional Modules

| Module                     | Primary Responsibility                                                | Inputs / Outputs                              |
| -------------------------- | --------------------------------------------------------------------- | --------------------------------------------- |
| Authentication Module      | Validate broker identity via OTP                                       | Email/Mobile, OTP / Access Token              |
| KYC Module                 | Capture and validate PAN, Aadhaar, GST, cancelled cheque, RERA, bank  | Documents, KYC data / KYC Status              |
| Project & Inventory Module | Maintain projects and plot availability, colour coding                | Project/Plot data / Availability Grid         |
| Customer Module            | Register and store customer details linked to a broker                | Customer details / Customer Record            |
| Booking Module             | Coordinate booking requests, token amount and payment mode            | Booking request / Booking Status              |
| Commission Module          | Compute commission, TDS and net payable; track releases               | Approved booking / Commission Ledger          |
| Notification Module        | Send notifications for projects, schemes and booking updates          | Event / Push Notification                     |
| Document Module            | Store and serve price lists, forms and documents                      | Request / Document File                       |
| Support Module             | Manage support tickets and relationship manager contacts              | Ticket details / Ticket Record                |
| Admin Module               | Manage projects, inventory, bookings, commissions and demand letters  | Admin actions / Updated master data           |
| Audit Logger               | Store activity logs for approvals and commission releases             | Events / Log File                             |

## Step 2: Modularization Analysis

The InventoryOne Broker Web App is decomposed into independent modules. The Authentication Module handles only broker verification, the KYC Module handles only broker verification documents, the Project & Inventory Module maintains plot availability, and the Booking Module is responsible only for creating and tracking booking requests. The Commission Module computes earnings independently, while the Notification Module is responsible only for delivering messages. This separation improves maintainability and enables independent testing of each module.

## Step 3: Coupling Analysis

| Module Interaction                              | Coupling           | Justification                                              |
| ----------------------------------------------- | ------------------ | ---------------------------------------------------------- |
| Authentication Module → OTP/SMS Gateway         | Message Coupling   | OTP request/response exchanged over a service API          |
| Booking Module → Project & Inventory Module     | Data Coupling      | Plot status (available/on hold/sold) exchanged             |
| Booking Module → Commission Module              | Data Coupling      | Approved booking details passed for computation            |
| Admin Module → Booking Module                   | Control Coupling   | Approve/reject command issued after review                 |
| Commission Module → Notification Module         | Data Coupling      | Commission settlement details received for messaging       |
| KYC Module → AWS S3                             | Message Coupling   | Document upload stored via object storage API              |
| Notification Module → Firebase Cloud Messaging  | Message Coupling   | Push messages delivered through an external service        |

## Step 4: Cohesion Analysis

The Authentication Module performs only authentication, the KYC Module performs only KYC verification, the Commission Module performs only commission/TDS computation and release tracking, and the Notification Module performs only message delivery. These modules therefore exhibit **functional cohesion**, the strongest and most desirable form of cohesion.

## Step 5: Function-Oriented vs Object-Oriented Design

| Aspect       | Function-Oriented                      | Object-Oriented                                            |
| ------------ | -------------------------------------- | ---------------------------------------------------------- |
| Focus        | Functions                              | Objects & Classes                                          |
| Reuse        | Limited                                | High                                                       |
| Maintenance  | Moderate                               | Easy                                                       |
| InventoryOne Example | `login()`, `bookPlot()`, `computeCommission()` | `Broker`, `Project`, `Plot`, `Customer`, `Booking`, `Commission` classes |

## Step 6: SOLID Principle Application

- **Single Responsibility Principle:** The Authentication Module performs only identity verification; the Commission Module performs only commission computation.
- **Open/Closed Principle:** New payment modes or plot status types can be added without modifying existing booking classes.
- **Liskov Substitution Principle:** Different notification channels (`Email`, `SMS`, `Push`) can replace the `Notification` abstraction.
- **Interface Segregation Principle:** Separate interfaces are provided for `DocumentStorage` (S3) and `OTPProvider` (SMS gateway).
- **Dependency Inversion Principle:** The Booking Module depends on `PaymentGateway` and `NotificationService` abstractions rather than concrete implementations.

## Step 7: Top-Down Design

Overall InventoryOne Broker Web App → Broker Authentication → Broker Dashboard → Project & Inventory View → Plot Details → Customer Registration → Booking Request → Company Approval → Commission Generation → Notification & Documents.

## Step 8: Bottom-Up Design

Develop Authentication, KYC, Project & Inventory, Customer and Commission modules independently. Integrate them through the Booking Module and finally connect them with the Broker Dashboard and the Admin Module.

---

# Design Analysis Report

The InventoryOne Broker Web App demonstrates effective modularity by separating responsibilities into independent modules such as Authentication, KYC, Project & Inventory, Booking and Commission. Functional cohesion is achieved within individual modules, while coupling is minimised through interface-based communication and message passing. Object-oriented design improves extensibility and maintainability, making it suitable for future enhancements such as QR-based bookings, biometric login, digital demand letters and integrated payment gateways.

---

## Observation

The InventoryOne Broker Web App architecture satisfies the characteristics of a good software design by providing high cohesion, low coupling, modular organization and clear separation of responsibilities across broker-facing and administrator-facing functions.

## Result

The InventoryOne Broker Web App was successfully analysed using software design principles. A structured design model and analysis report were prepared demonstrating the applicability of modularization, abstraction, information hiding, cohesion, coupling and object-oriented design concepts.
