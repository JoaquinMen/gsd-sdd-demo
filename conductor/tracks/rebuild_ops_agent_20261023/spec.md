# Track Specification: Rebuild Enterprise Operations & HR Intelligence Agent Platform

## 1. Overview & Context

This track rebuilds the **Enterprise Operations & HR Intelligence Agent Platform** in this workspace using the Single Source of Truth specification defined in [`prev-engagements/SPEC.md`](../../prev-engagements/SPEC.md).

The solution implements a unified conversational web application built on Google Agent Development Kit (ADK) Web and Vertex AI (`gemini-3.5-flash`), with dual specialized backend tool integrations:
1. **Unstructured Search Tool (`VertexAiSearchTool`)**: Grounded semantic retrieval over regional HR policy documents in Vertex AI Search (Discovery Engine), using `bypass_multi_tools_limit=True` for function coexistence.
2. **Structured Query Toolset (`BigQueryToolset`)**: Analytical SQL querying with non-bypassable read-only protection (`WriteMode.BLOCKED`) against partitioned BigQuery billing tables.
3. **Automated Provisioning Pipeline**: Dynamic PDF generation, Cloud Storage staging, Discovery Engine indexing, and rolling date BigQuery table seeding.

---

## 2. Functional Requirements

### 2.1 Configuration & Bootstrap Engine
- Encapsulate environment variables in `AppConfig` dataclass with startup validation.
- Implement `_ensure_ssl_cert_file` to point `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` to a valid CA bundle (`certifi.where()` or `/etc/ssl/cert.pem`).

### 2.2 Unstructured Search Tool (`src/agent/tools/search_tool.py`)
- Instantiate `VertexAiSearchTool` pointing to `<DATASTORE_ID>` with `bypass_multi_tools_limit=True`.
- Expose `discovery_engine_search` function declaration to Gemini without conflicting with custom tool functions.

### 2.3 Structured Analytics Toolset (`src/agent/tools/billing_tool.py`)
- Instantiate `BigQueryToolset` with `BigQueryToolConfig(write_mode=WriteMode.BLOCKED)`.
- Enforce Application Default Credentials (`google.auth.default()`).

### 2.4 Prompt & Agent Orchestration (`src/agent/prompts.py` & `src/agent/agent.py`)
- `build_system_prompt`: Inject domain routing rules, fully qualified BigQuery table schema, column definitions, `is_billable` rules, revenue calculation formula `SUM(hours_billed * hourly_rate_usd)`, and strict anti-hallucination/citation rules.
- `build_root_agent`: Build `LlmAgent(name="operations_router_agent", model=cfg.gemini_model, ...)` with `canonical_model.client_kwargs = {"location": "global"}`.
- Export `root_agent` at module level for ADK Web discovery.

### 2.5 Automated Provisioning Pipeline (`src/provisioning/`)
- `generate_documents.py`: Generate 3 synthetic policy PDFs (`regional_holidays.pdf`, `benefits_jurisdiction_a.pdf`, `benefits_jurisdiction_b.pdf`) with structured tables and policies via `fpdf2`.
- `setup_discovery_engine.py`: Provision GCS bucket, upload PDFs, ensure Discovery Engine DataStore exists, and trigger `import_documents` with `ReconciliationMode.INCREMENTAL`.
- `seed_warehouse.py`: Create BigQuery dataset and table (partitioned by `work_date`, clustered by `project_id, consultant_name, country`), generating rolling dates relative to `datetime.date.today()` with `WRITE_TRUNCATE`.
- `setup_all.py`: Orchestrator CLI coordinating all stages with `--wait` and selective skip flags.
- `verify_e2e.py`: Live smoke verification script checking BigQuery, Discovery Engine, and ADK agent routing.

---

## 3. Non-Functional Requirements

- **Security & Data Protection**: Zero hardcoded credentials; ADC only; `WriteMode.BLOCKED` database protection.
- **Test Coverage**: Comprehensive unit test suite with 100% mocked GCP dependencies targeting `>80%` test coverage.
- **Portability**: All cloud parameters externalized to `.env` with a clean `.env.example` template.

---

## 4. Acceptance Criteria

- All unit tests pass with `pytest -v tests/`.
- `terraform -chdir=terraform validate` succeeds (0 errors).
- Application compiles cleanly and adheres to google-adk conventions.
- Zero customer IP or proprietary data present in the codebase.
