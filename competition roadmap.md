**Document Control**

* **Document Title:** Altman Z-Score Feature Requirements
* **Version:** 1.0
* **Date:** May 30, 2025
* **Author:** Fabio Correa / Generative Ideas

---

# Vision Alignment

All competitive planning and feature requirements are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

---

# 1. Introduction

## 1.1 Purpose

This Requirements Document defines the functional and non-functional requirements for the Altman Z-Score tool roadmap aimed at achieving best-in-class capabilities.

## 1.2 Scope

Covers features across five phases: Foundation, Interactivity, Intelligence, Enterprise & Extensibility, and Scale & Partnerships. Excludes internal infrastructure upgrades and non-customer-facing maintenance.

## 1.3 Stakeholders

* **Sole Team Member & Producer:** Fabio Correa

---

# 2. Overall Description

## 2.1 System Context

The Altman Z-Score tool is an open-source Python package with CLI, API, and dashboard interfaces for calculating and analyzing corporate distress scores.

## 2.2 User Profiles

* **Quantitative Analysts:** Batch processing and calibration
* **Financial Analysts:** Interactive dashboards and narrative summaries
* **Risk Managers:** Alerts and compliance reporting
* **Enterprise IT:** BI integrations and SaaS deployment

---

## 2.3 Competitive Differentiators

To ensure we outpace best-in-class commercial platforms, Altman Z-Score will leverage:

* **Zero Licensing Cost:** Fully open-source core with optional add-ons under open‑core licensing, undercutting subscription fees.
* **Modular Data Flexibility:** Plug-and-play connectors for free and premium data sources to meet diverse user needs.
* **AI-Driven Insights:** Automated narrative summaries and alerting to accelerate decision-making and reduce manual analysis.
* **Community-Driven Roadmap:** Public roadmap, contribution sprints, and early access programs to rapidly iterate based on user feedback.
* **Enterprise Packaging:** Optional hosted SaaS tier with SLAs, role-based access, audit-ready reporting, and BI integrations to match institutional requirements.

---

# 3. Functional Requirements

## Phase 1: Foundation

* **REQ-1.1:** Modular Data Connectors

  * **Description:** Support ingestion from multiple data sources (e.g., Alpha Vantage, IEX Cloud, CSV, SQL, REST).
  * **Priority:** High

* **REQ-1.2:** Public REST API v1

  * **Description:** Expose Z-Score calculations and metadata via RESTful endpoints.
  * **Priority:** High

* **REQ-1.3:** Enhanced CLI

  * **Description:** Batch processing interface allowing per-ticker outputs and summary reports.
  * **Priority:** Medium

* **REQ-1.4:** Documentation & Tutorials

  * **Description:** Updated documentation site with quickstarts, in-tool help, and guided tutorials.
  * **Priority:** Medium

## Phase 2: Interactivity

* **REQ-2.1:** Web Dashboard

  * **Description:** Interactive UI with drill-down charts (trend, scatter, heatmaps) and peer comparisons.
  * **Priority:** High

* **REQ-2.2:** Excel Add-In

  * **Description:** One-click report generation from Excel, embedding Z-Score results and visualizations.
  * **Priority:** Medium

* **REQ-2.3:** Alerting System

  * **Description:** Configurable email and Slack notifications based on user-defined thresholds.
  * **Priority:** Medium

## Phase 3: Intelligence

* **REQ-3.1:** AI Narrative Generation

  * **Description:** LLM-powered plain-English summaries of Z-Score movements and risk drivers.
  * **Priority:** High

* **REQ-3.2:** SaaS Tier

  * **Description:** Hosted deployment with basic SLAs and role-based access controls.
  * **Priority:** Medium

## Phase 4: Enterprise & Extensibility

* **REQ-4.1:** Pro Plugins

  * **Description:** Premium modules for advanced stress-testing and scenario analysis under an open-core model.
  * **Priority:** Medium

* **REQ-4.2:** Audit-Ready Exports

  * **Description:** Report exports with versioning, change logs, and metadata for compliance.
  * **Priority:** Medium

* **REQ-4.3:** BI Platform Integrations

  * **Description:** Custom visuals for Power BI and connectors for Tableau.
  * **Priority:** Medium

* **REQ-4.4:** Marketplace Deployment

  * **Description:** Listings in cloud marketplaces (e.g., Azure Marketplace) with automated deployment scripts.
  * **Priority:** Low

## Phase 5: Scale & Partnerships

* **REQ-5.1:** Real-Time Data Feeds

  * **Description:** WebSocket support and partnerships for direct premium data feeds.
  * **Priority:** Medium

* **REQ-5.2:** Enhanced API v2

  * **Description:** Bulk endpoints, streaming support, and improved request handling.
  * **Priority:** Low

* **REQ-5.3:** Mobile-Responsive UI

  * **Description:** Dashboard optimized for mobile devices.
  * **Priority:** Low

---

# 4. Non-Functional Requirements

* **NFR-1:** Performance

  * System must process large batches (e.g., 100 tickers) efficiently.

* **NFR-2:** Security

  * SaaS tier and APIs must enforce OAuth2 and TLS encryption.

* **NFR-3:** Scalability

  * Architecture must support horizontal scaling for API and UI components.

* **NFR-4:** Usability

  * Documentation and interfaces should target a System Usability Scale (SUS) score ≥ 80.

* **NFR-5:** Reliability

  * SaaS uptime commitment to meet organizational standards.

