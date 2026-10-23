# Product Guide: Cimbal SA Secure Operations & Agriculture Intelligence Platform

## Vision
The Cimbal SA Secure Operations Platform is an enterprise-grade conversational AI assistant designed for Cimbal SA—a leading retail and field service company specializing in agricultural machinery (tractors, combine harvesters, planters, sprayers). The platform enables field technicians, dealership managers, and operations personnel to query both unstructured equipment documentation (operator manuals, warranty coverage guidelines, regional service rates) and structured operational databases (field service billing logs, technician labor hours, parts costs) in a single unified interface.

## Security Mandates
- **Perimeter Defense**: Zero public exposure of backend databases or models.
- **Identity-Aware Proxy (IAP)**: Direct IAP enabled on Cloud Run with cryptographic server-side validation of `X-Goog-IAP-JWT-Assertion`.
- **Network Isolation**: All outbound traffic routes through a custom VPC using **Direct VPC Egress** and **Private Google Access** to communicate with Vertex AI, BigQuery, and Discovery Engine over Google's private network backbone.
- **Read-Only Data Governance**: Programmatic enforcement (`WriteMode.BLOCKED`) preventing any non-`SELECT` database mutations.

## Target User Personas
- **Field Service Technicians**: Look up troubleshooting steps, hydraulic specs, warranty limits, and log billable service hours from the field.
- **Dealership Service Managers**: Track labor utilization, verify warranty claim classifications, audit emergency rate multipliers (1.5x during harvest season), and monitor regional parts expenses.
- **Operations & Finance Directors**: Analyze operational service revenue, customer vs. warranty split, and technician productivity across regional dealership hubs.

## Core Capabilities
1. **Custom FastAPI Web Portal**: Replaces generic ADK Web with a branded, responsive corporate portal displaying authenticated employee identity badges and streaming real-time responses.
2. **Dual-Domain Reasoning (`gemini-3.5-flash`)**: Dynamically routes questions across unstructured Discovery Engine search and structured BigQuery analytical SQL within a single conversational turn.
3. **Automated Provisioning**: Idempotent generation of agricultural equipment documentation, Cloud Storage staging, Discovery Engine indexing, and rolling date BigQuery table seeding.
