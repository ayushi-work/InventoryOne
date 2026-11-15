# Experiment 2: Problem Identification and Feasibility: Software Design Principles

## Aim

To identify the problem addressed by the selected software project and prepare its problem statement, objectives, scope, and technical and operational feasibility analysis.

## Objectives

- Identify the real-world problem addressed by the software project.
- Prepare a clear problem statement.
- Define project objectives and scope.
- Perform technical and operational feasibility analysis.
- Evaluate the viability of the proposed solution.

## Introduction

Problem identification is the first step in software engineering. A well-defined problem statement and feasibility study ensure that the proposed software solution is practical, achievable and aligned with stakeholder requirements before development begins.

## Selected Project

**Project Title:** InventoryOne — Broker Web App

**Domain:** Real Estate / Property Management

## Problem Statement

Traditional real-estate plot booking relies on manual coordination between brokers and the company, resulting in stale inventory data, delayed booking confirmations, and no clear visibility of plot availability or commissions. Brokers must contact the company office to check availability, raise bookings over phone or email, and track their earnings through spreadsheets — a slow, error-prone process that also limits service hours.

The proposed **InventoryOne — Broker Web App** provides a secure, self-service digital platform where each broker can log in with OTP verification, complete KYC, view active projects with live colour-coded plot availability, register customers, and raise booking requests directly at any time. The system enables the company administrator to approve or reject bookings, while brokers can track commissions, download documents, and stay updated through notifications.

## Project Objectives

- Provide secure broker authentication using OTP-based login and KYC verification.
- Display active projects with live, colour-coded plot availability (Available / Booked / Hold / Cancel).
- Enable customer registration and raise booking requests with company approval.
- Compute and track broker commissions (percentage, TDS, net payable).
- Provide downloadable documents and real-time notifications.
- Reduce manual coordination, waiting time and improve booking *transparency*.

## Project Scope

The InventoryOne: Broker Web App supports broker registration and KYC, project and plot inventory viewing, customer registration, booking requests with company approval, commission management, document downloads, notifications and support tickets. Administrative maintenance activities such as project management, plot inventory management and booking approval are included. Customer-facing portals, loan processing, account creation for customers and native mobile applications are outside the scope of this project.

## Technical Feasibility Analysis

| Factor       | Assessment | Remarks                                                        |
| ------------ | ---------- | -------------------------------------------------------------- |
| Technology   | Feasible   | Next.js + TypeScript, Django + DRF, PostgreSQL and Redis support development |
| Hardware     | Feasible   | Standard PCs and modern web browsers are sufficient            |
| Software Tools | Feasible | VS Code, Git, GitHub, Postman, Draw.io and Django Admin available |
| Security     | Feasible   | OTP authentication, KYC validation and HTTPS-encrypted communication can be implemented |
| Scalability  | Feasible   | Modular client–server architecture supports future enhancements |

## Operational Feasibility Analysis

| Factor            | Assessment | Remarks                                                  |
| ----------------- | ---------- | -------------------------------------------------------- |
| User Acceptance   | High       | Simple and familiar web interface                        |
| Ease of Use       | High       | Minimal training required                                |
| Availability      | High       | 24×7 online access from any device                       |
| Maintainability   | High       | Modular design simplifies maintenance                    |
| Business Benefit  | High       | Faster bookings and transparent commissions improve broker satisfaction and operational efficiency |

## Analysis

The feasibility study indicates that the InventoryOne — Broker Web App is technically and operationally viable. Existing technologies, development tools and real-estate business practices adequately support successful implementation.

## Observation

Clearly defining the problem, objectives, scope and feasibility provides a strong foundation for subsequent software design and development activities.

## Result

The problem statement, objectives, project scope, and technical and operational feasibility analysis for the InventoryOne — Broker Web App were successfully prepared.
