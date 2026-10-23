# Track Specification: Safe Agent App (`safe_agent_app_20261023`)

## 1. Overview & Context

The **Safe Agent App** track builds a secure, production-grade conversational application powered by the **Google Agent Development Kit (ADK) Web** framework and **Vertex AI (`gemini-3.5-flash`)**.

The platform enables enterprise users (operations staff, finance managers, consultants) to query both unstructured policy handbooks and structured analytical data warehouses through a single conversational interface while enforcing non-negotiable enterprise safety guardrails:

- **Strict Read-Only Database Protection**: Programmatically blocking any data-mutating SQL operations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`) against analytical tables via `WriteMode.BLOCKED`.
- **TLS/mTLS & SecureConnect Hardening**: Pre-flight bootstrap verifying system CA certificate bundles (`certifi` / `/etc/ssl/cert.pem`) across synchronous and asynchronous streaming requests (`httpx.AsyncClient`).
- **Grounded Semantic Retrieval & Anti-Hallucination**: Vertex AI Search (Discovery Engine) chunk-level grounding with mandatory source document citations.
- **Zero Static Credentials**: 100% Application Default Credentials (ADC) identity model with least-privilege IAM role bindings.
- **Idempotent Automated Provisioning**: Repeatable pipelines for generating standardized policy PDFs, Cloud Storage staging, search datastore ingestion, and dynamic BigQuery table seeding.

---

## 2. Functional Requirements

### 2.1 Configuration & Security Bootstrap (`src/agent/config.py`)
- **`AppConfig` Dataclass**: Frozen configuration reading and validating all runtime environment variables (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_GENAI_USE_VERTEXAI`, `GEMINI_MODEL`, `BQ_DATASET_ID`, `BQ_TABLE_ID`, `GCS_HR_BUCKET`, `VERTEX_SEARCH_LOCATION`, `VERTEX_SEARCH_DATASTORE_ID`).
- **Calculated Properties**: Expose `bq_table_fqn` (`<project>.<dataset>.<table>`) and `vertex_search_datastore_path`.
- **`_ensure_ssl_cert_file`**: Guarantee `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` environment variables point to an accessible certificate authority bundle before initializing any HTTP/mTLS clients.

### 2.2 Unstructured Policy Search Tool (`src/agent/tools/search_tool.py`)
- Instantiate `VertexAiSearchTool` referencing the configured Discovery Engine datastore path.
- Enable `bypass_multi_tools_limit=True` to allow ADK to expose Discovery Engine as a callable function (`discovery_engine_search`) alongside custom tool declarations without triggering Vertex AI API coexistence errors.

### 2.3 Hardened Structured BigQuery Toolset (`src/agent/tools/billing_tool.py`)
- Acquire credentials via `google.auth.default()`.
- Wrap in `BigQueryToolset` configured with `BigQueryToolConfig(write_mode=WriteMode.BLOCKED)`.
- Programmatically reject any DDL/DML mutation attempt before job submission to BigQuery.

### 2.4 Grounded System Prompt & Guardrails (`src/agent/prompts.py`)
- Ingest table schema, column descriptions, and valid partition fields.
- Instruct the model to:
  1. Calculate revenue metrics using `SUM(hours_billed * hourly_rate_usd)`.
  2. Disambiguate client-billable hours (`WHERE is_billable = TRUE`) from internal operational tasks.
  3. Ground every policy statement in returned search chunks, citing document names and jurisdictions.
  4. Explicitly declare when an HR policy is absent from the indexed corpus.

### 2.5 Root Router Agent (`src/agent/agent.py` & `src/agent/__init__.py`)
- Assemble `LlmAgent(name="safe_agent_app_router", model=cfg.gemini_model, tools=[...], instruction=...)`.
- Bind `agent.canonical_model.client_kwargs = {"location": "global"}` for Vertex AI publisher endpoints.
- Export `root_agent` at the `src/agent` module root for seamless discovery by `adk web .`.

### 2.6 Data Provisioning & Seeding Pipeline (`src/provisioning/`)
- `generate_documents.py`: Programmatically generate 3 standardized policy PDFs (`regional_holidays.pdf`, `benefits_jurisdiction_a.pdf`, `benefits_jurisdiction_b.pdf`) using `fpdf2`.
- `setup_discovery_engine.py`: Idempotently create `gs://<BUCKET_NAME>`, upload PDFs, ensure Discovery Engine DataStore exists, and import documents with `ReconciliationMode.INCREMENTAL`.
- `seed_warehouse.py`: Create BigQuery dataset and table (partitioned by `work_date`, clustered by `project_id, consultant_name, country`), dynamically seeding records relative to `datetime.date.today()` with `WriteDisposition.WRITE_TRUNCATE`.
- `setup_all.py`: Orchestrator CLI coordinating all stages with `--wait` and selective skip flags.
- `verify_e2e.py`: Live smoke verification script checking BigQuery, Discovery Engine, and ADK agent routing.

---

## 3. Non-Functional Requirements & Security Controls

| Security / Operational Domain | Implementation & Enforcement Mechanism |
| :--- | :--- |
| **Database Write Protection** | `BigQueryToolConfig(write_mode=WriteMode.BLOCKED)` programmatically prevents `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`. |
| **Authentication & IAM** | Application Default Credentials (`google.auth.default()`) with zero static keys in code or `.env`. Least-privilege roles for runtime vs. provisioning. |
| **Transport Security (TLS/mTLS)** | `_ensure_ssl_cert_file` validates CA certificate paths for secure SSE streaming and API RPCs. |
| **Anti-Hallucination** | System prompt mandates explicit citations and disallows speculative extrapolations when chunks lack requested data. |
| **Test Coverage & Quality** | 100% mocked unit test suite covering configuration, tools, prompts, routing, and provisioning with `>80%` code coverage. |

---

## 4. Acceptance Criteria

- [ ] All unit tests pass with `pytest -v tests/`.
- [ ] Attempting a non-`SELECT` query via `BigQueryToolset` triggers a blocked-write validation failure.
- [ ] `VertexAiSearchTool` is initialized with `bypass_multi_tools_limit=True`.
- [ ] Dynamic date calculation ensures BigQuery test fixtures remain valid across rolling date windows.
- [ ] Zero hardcoded secrets, customer project IDs, or PII exist in the codebase.
- [ ] `adk web .` starts and loads `root_agent` without import or discovery errors.
