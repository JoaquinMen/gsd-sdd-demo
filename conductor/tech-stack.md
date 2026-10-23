# Technology Stack

## Core Technologies
- **Language**: Python 3.11+
- **Agent Framework**: Google Agent Development Kit (`google-adk`) Web
- **Generative AI & Foundation Models**: Google GenAI SDK (`google-genai`), Vertex AI `gemini-3.5-flash` (routed via global publisher endpoint)
- **Data & Analytics**:
  - Google Cloud BigQuery (`google-cloud-bigquery`) for structured time tracking logs and analytical querying
  - Vertex AI Search / Discovery Engine (`google-cloud-discoveryengine`) for unstructured PDF semantic retrieval
  - Google Cloud Storage (`google-cloud-storage`) for policy document staging
- **Web & Serving Runtime**: FastAPI, Uvicorn, Server-Sent Events (SSE)
- **Document Generation**: `fpdf2` for synthetic policy PDF generation
- **Infrastructure as Code (IaC)**: Terraform 1.6+ (Google provider)
- **Containerization**: Docker (distroless / multi-stage build)
- **Testing & Quality Assurance**: `pytest`, `pytest-asyncio`, `pytest-mock`
