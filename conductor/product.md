# Initial Concept
Rebuild the Enterprise Operations & HR Intelligence Agent platform based on the solution specification in prev-engagements/SPEC.md.

# Product Guide

## Vision
The Enterprise Operations & HR Intelligence Agent is a unified conversational operational intelligence platform built with the Google Agent Development Kit (ADK) and Vertex AI. It bridges unstructured organizational knowledge (regional holiday schedules, leave policies, benefits handbooks) with structured transactional data (analytical time-tracking, consultant billing hours, project rates) in a single-agent, multi-tool architecture.

## Target Users
- **Operations & Finance Leads**: Tracking project billing hours, revenue totals, consultant utilization, and rate multipliers across client engagements.
- **People Operations / HR Specialists**: Answering employee inquiries regarding cross-border holiday schedules, parental/maternity/paternity leave, PTO accruals, and health benefits.
- **Engagement Managers & Delivery Consultants**: Verifying billing compliance, checking project time logs, and reviewing regional holiday billing policies.

## Core Features & Capabilities
1. **Unified Natural Language Routing**: Dynamic, single-turn query routing between unstructured document retrieval and structured SQL execution powered by `gemini-3.5-flash`.
2. **Read-Only Data Governance**: Hard programmatic protection (`WriteMode.BLOCKED`) preventing any non-`SELECT` database mutations against analytical billing tables.
3. **Grounded Policy Retrieval**: Semantic search with document chunk citations over regional policy documents indexed in Vertex AI Search (Discovery Engine).
4. **Cross-Domain Synthesis**: Answering complex inquiries that correlate policy guidelines (e.g., statutory holiday rates) with transactional time records in a single turn.
5. **Automated Provisioning Pipeline**: Idempotent document generation, Cloud Storage staging, Discovery Engine indexing, and BigQuery data seeding with dynamic rolling dates.
