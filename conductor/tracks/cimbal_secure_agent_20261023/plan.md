# Implementation Plan: Cimbal SA Secure Operations & Agriculture Intelligence Agent

This plan guides the step-by-step implementation of the Cimbal SA Secure Operations platform following the Conductor workflow and Test-Driven Development (TDD).

---

## Phase 1: Infrastructure as Code & VPC Network Blueprint

- [x] Task: Project Manifests & Configuration Templates (f98ff04)
    - [x] Create `pyproject.toml` and pinned `requirements.txt` with FastAPI, Google GenAI, ADK, and GCP SDKs
    - [x] Create `.env.example` documenting all VPC, Direct IAP, model, and dataset variables
    - [x] Verify dependencies install cleanly and environment loads properly

- [x] Task: Terraform VPC, Subnet, and Cloud Run Direct IAP Modules (e456f21)
    - [x] Implement `terraform/modules/vpc/` with custom VPC network and subnet configured for Private Google Access
    - [x] Implement `terraform/modules/cloud_run/` configured with `iap_enabled = true` and Direct VPC Egress
    - [x] Implement `terraform/modules/iam/` granting `roles/run.invoker` to the IAP Service Agent
    - [x] Implement `terraform/modules/bigquery/` and `terraform/modules/storage/` for Cimbal data assets
    - [x] Implement root `terraform/main.tf`, `variables.tf`, and `outputs.tf`
    - [x] Run `terraform -chdir=terraform validate` to verify syntax

- [ ] Task: Conductor - User Manual Verification 'Infrastructure as Code & VPC Network Blueprint' (Protocol in workflow.md)

---

## Phase 2: Domain Provisioning Pipeline (Cimbal SA Equipment)

- [x] Task: Equipment Documentation & Warranty PDF Generator (bd6c013)
    - [x] Write unit test in `tests/test_document_generator.py` asserting generated PDF content for Cimbal equipment
    - [x] Implement `src/provisioning/generate_documents.py` creating 3 PDFs (`equipment_warranty_guidelines.pdf`, `machinery_operator_manuals.pdf`, `regional_service_rates.pdf`)
    - [x] Verify test passes and PDFs are generated in `data/equipment_docs/`

- [x] Task: Cloud Storage Staging & Discovery Engine Datastore Pipeline (b973e67)
    - [x] Write unit test in `tests/test_setup_discovery_engine.py` mocking GCS upload and Discovery Engine import
    - [x] Implement `src/provisioning/setup_discovery_engine.py` with idempotent bucket creation and document import
    - [x] Verify test passes with mocked GCP services

- [x] Task: BigQuery Equipment Service Billing Seeding Pipeline (59bc98c)
    - [x] Write unit test in `tests/test_seed_warehouse.py` asserting rolling dynamic dates, 13-column schema, and equipment models
    - [x] Implement `src/provisioning/seed_warehouse.py` seeding `cimbal_operations.equipment_service_billing` using `WRITE_TRUNCATE`
    - [x] Verify test passes confirming dynamic date generation

- [x] Task: Unified Provisioning CLI (f76155e)
    - [x] Implement `src/provisioning/setup_all.py` coordinating PDF generation, search setup, and BQ seeding
    - [x] Add CLI arguments for `--wait`, `--skip-pdfs`, `--skip-search`, and `--skip-bigquery`
    - [x] Verify CLI help and compilation

- [ ] Task: Conductor - User Manual Verification 'Domain Provisioning Pipeline (Cimbal SA Equipment)' (Protocol in workflow.md)

---

## Phase 3: Secure FastAPI Agent Runtime & IAP Middleware

- [ ] Task: App Configuration & TLS Bootstrap
    - [ ] Write unit test in `tests/test_config.py` verifying config loading and SSL cert resolution
    - [ ] Implement `src/agent/config.py` with `AppConfig` and `_ensure_ssl_cert_file`
    - [ ] Verify tests pass for both valid configuration and missing variable errors

- [ ] Task: IAP Cryptographic JWT Verification Middleware
    - [ ] Write unit test in `tests/test_iap_middleware.py` testing valid JWT signature, expired token rejection, and mock dev bypass
    - [ ] Implement `src/agent/middleware/iap.py` validating `X-Goog-IAP-JWT-Assertion` and extracting user claims
    - [ ] Verify middleware tests pass

- [ ] Task: Modular Agent Tools (Search Tool & Read-Only Billing Toolset)
    - [ ] Write unit test in `tests/test_agent_tools.py` asserting `bypass_multi_tools_limit=True` and `WriteMode.BLOCKED`
    - [ ] Implement `src/agent/tools/search_tool.py` using `VertexAiSearchTool`
    - [ ] Implement `src/agent/tools/billing_tool.py` using `BigQueryToolset` and ADC credentials
    - [ ] Verify tools initialize with correct parameters and mutation queries are rejected

- [ ] Task: Router System Prompt & Root Agent Assembly
    - [ ] Write unit test in `tests/test_agent_router.py` asserting system prompt, model configuration, and tool binding
    - [ ] Implement `src/agent/prompts.py` tailored for Cimbal equipment operations, warranty guidelines, and rate calculations
    - [ ] Implement `src/agent/agent.py` assembling `LlmAgent` with `gemini-3.5-flash` (`location="global"`)
    - [ ] Verify agent compiles and exports `root_agent`

- [ ] Task: Conductor - User Manual Verification 'Secure FastAPI Agent Runtime & IAP Middleware' (Protocol in workflow.md)

---

## Phase 4: Custom Frontend & Real-Time SSE Stream

- [ ] Task: Custom Frontend Templates & Static Assets
    - [ ] Create Jinja2 templates in `src/agent/templates/index.html` with Cimbal SA branding, employee profile badge, and chat container
    - [ ] Create CSS styling in `src/agent/static/css/style.css` and JavaScript in `src/agent/static/js/app.js`
    - [ ] Verify template renders user profile and chat UI

- [ ] Task: FastAPI Application & SSE Chat Endpoint
    - [ ] Write unit test in `tests/test_app.py` verifying `/healthz`, `/`, and `/api/v1/chat/stream` routes
    - [ ] Implement `src/agent/main.py` assembling FastAPI app, mounting static files, registering IAP middleware, and streaming responses
    - [ ] Verify streaming route dispatches to `Runner.run_async` and yields formatted SSE events

- [ ] Task: Conductor - User Manual Verification 'Custom Frontend & Real-Time SSE Stream' (Protocol in workflow.md)

---

## Phase 5: Verification Suite & Quality Assurance

- [ ] Task: Comprehensive Unit Test Suite
    - [ ] Implement `tests/conftest.py` with mock environments and GCP client patches
    - [ ] Run `pytest -v tests/` and confirm 100% pass rate
    - [ ] Confirm code coverage exceeds 80%

- [ ] Task: Live End-to-End Smoke Verification CLI
    - [ ] Implement `src/provisioning/verify_e2e.py` testing live BigQuery query, Discovery Engine search, and ADK invocation
    - [ ] Verify CLI handles credentials and outputs diagnostic summaries

- [ ] Task: Conductor - User Manual Verification 'Verification Suite & Quality Assurance' (Protocol in workflow.md)
