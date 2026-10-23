# Technology Stack: Cimbal SA Secure Operations Platform

## Core Languages & Frameworks
- **Programming Language**: Python 3.11+
- **Agent Framework**: Google Agent Development Kit (`google-adk`) Web
- **Web & Serving Runtime**: FastAPI `>=0.110.0`, Uvicorn `>=0.29.0`, Jinja2 (HTML templates), Server-Sent Events (SSE)
- **Foundation Model**: Vertex AI `gemini-3.5-flash` via `google-genai` (routed to `global` publisher endpoint)
- **Authentication**: Direct Identity-Aware Proxy (IAP) on Cloud Run (`iap_enabled = true`) + `PyJWT` / `cryptography` for ES256 verification

## Google Cloud Infrastructure & Services
- **Serverless Compute**: Google Cloud Run with Direct VPC Egress
- **Networking**: Custom VPC (`10.0.0.0/16`), dedicated Direct Egress Subnet (`10.0.1.0/24`), Private Google Access (PGA)
- **Unstructured Search**: Vertex AI Search / Discovery Engine (`google-cloud-discoveryengine`)
- **Analytical Data Warehouse**: Google Cloud BigQuery (`google-cloud-bigquery`)
- **Object Storage**: Google Cloud Storage (`google-cloud-storage`)
- **Document Generation**: `fpdf2`
- **Infrastructure as Code (IaC)**: Terraform 1.6+ (Google & Google-Beta providers)

## Quality Assurance & Testing
- **Test Runner**: `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `pytest-mock>=3.12.0`
- **Coverage Target**: `>80%` statement coverage across all core modules
