# Implementation Plan: Rebuild Enterprise Operations & HR Intelligence Agent Platform

This plan tracks the phased implementation of the Enterprise Operations & HR Intelligence Agent platform following the Conductor workflow and Test-Driven Development (TDD).

---

## Phase 1: Project Environment & Infrastructure Scaffolding

- [ ] Task: Project Manifests & Configuration Templates
    - [ ] Create `pyproject.toml` and pinned `requirements.txt` with ADK, GenAI, and GCP dependencies
    - [ ] Create `.env.example` documenting all runtime and provisioning variables
    - [ ] Verify package installation and environment consistency

- [ ] Task: Terraform Infrastructure as Code Modules
    - [ ] Implement `terraform/modules/bigquery/` with partitioned and clustered billing table
    - [ ] Implement `terraform/modules/storage/` with versioned staging bucket
    - [ ] Implement `terraform/modules/discovery_engine/` with unstructured search dataStore
    - [ ] Implement `terraform/modules/iam/` with least-privilege service account role bindings
    - [ ] Implement root `terraform/main.tf`, `variables.tf`, and `outputs.tf`
    - [ ] Run `terraform init` and `terraform validate` to verify configuration syntax

- [ ] Task: Conductor - User Manual Verification 'Project Environment & Infrastructure Scaffolding' (Protocol in workflow.md)

---

## Phase 2: Automated Data & Discovery Provisioning Pipeline

- [ ] Task: Policy Document Synthesis Engine
    - [ ] Write unit test in `tests/test_document_generator.py` asserting PDF page structure and content
    - [ ] Implement `src/provisioning/generate_documents.py` using `fpdf2` generating 3 policy PDFs
    - [ ] Verify test passes and generated PDFs exist in target staging directory

- [ ] Task: Cloud Storage & Discovery Engine Pipeline
    - [ ] Write unit test in `tests/test_setup_discovery_engine.py` mocking GCS and Discovery Engine clients
    - [ ] Implement `src/provisioning/setup_discovery_engine.py` with idempotent bucket provisioning and `import_documents`
    - [ ] Verify tests pass with 100% mocked calls

- [ ] Task: BigQuery Analytical Seeding Engine
    - [ ] Write unit test in `tests/test_seed_warehouse.py` asserting rolling dynamic dates and schema columns
    - [ ] Implement `src/provisioning/seed_warehouse.py` with `WRITE_TRUNCATE` load job and 13-column schema
    - [ ] Verify tests pass confirming dynamic date calculation relative to `datetime.date.today()`

- [ ] Task: Master Provisioning Orchestrator
    - [ ] Implement `src/provisioning/setup_all.py` coordinating PDF generation, search setup, and BQ seeding
    - [ ] Add CLI arguments for `--wait`, `--skip-pdfs`, `--skip-vertex-search`, and `--skip-bigquery`
    - [ ] Verify CLI compiles and help documentation renders properly

- [ ] Task: Conductor - User Manual Verification 'Automated Data & Discovery Provisioning Pipeline' (Protocol in workflow.md)

---

## Phase 3: Conversational Agent Runtime & Modular Tools

- [ ] Task: App Configuration & TLS/mTLS Bootstrap Engine
    - [ ] Write unit tests in `tests/test_config.py` verifying `AppConfig` parsing, validation, and SSL cert logic
    - [ ] Implement `src/agent/config.py` with `AppConfig` dataclass and `_ensure_ssl_cert_file`
    - [ ] Verify tests pass for both valid environment and missing variable error cases

- [ ] Task: Unstructured Search Tool with Coexistence Flag
    - [ ] Write unit test in `tests/test_agent_tools.py` verifying `VertexAiSearchTool` instantiation
    - [ ] Implement `src/agent/tools/search_tool.py` setting `bypass_multi_tools_limit=True`
    - [ ] Verify search tool initializes with correct datastore resource path

- [ ] Task: Read-Only Analytical BigQuery Toolset
    - [ ] Write unit test in `tests/test_agent_tools.py` asserting `WriteMode.BLOCKED` enforcement
    - [ ] Implement `src/agent/tools/billing_tool.py` using `BigQueryToolset` and ADC credentials
    - [ ] Verify mutation queries (`INSERT`, `DROP`) are rejected prior to execution

- [ ] Task: Router System Prompt & Routing Rules
    - [ ] Write unit test verifying system prompt contains required FQN, column metadata, and citation rules
    - [ ] Implement `src/agent/prompts.py` with `build_system_prompt()` injecting table schema and domain boundaries
    - [ ] Verify generated prompt string adheres to anti-hallucination and revenue calculation guidelines

- [ ] Task: Root Router Agent Assembly & ADK Discovery Entrypoint
    - [ ] Write unit test in `tests/test_agent_router.py` asserting `LlmAgent` configuration and model location
    - [ ] Implement `src/agent/agent.py` configuring `LlmAgent` with `gemini-3.5-flash` (`location="global"`)
    - [ ] Export `root_agent` in `src/agent/__init__.py` for ADK Web discovery (`adk web .`)
    - [ ] Verify agent package imports and instantiates cleanly

- [ ] Task: Conductor - User Manual Verification 'Conversational Agent Runtime & Modular Tools' (Protocol in workflow.md)

---

## Phase 4: Automated Verification Suite & Quality Gates

- [ ] Task: Comprehensive Unit Test Suite
    - [ ] Implement `tests/conftest.py` with mock environments and patch fixtures
    - [ ] Execute `pytest -v tests/` and verify 100% test pass rate
    - [ ] Verify statement coverage exceeds 80%

- [ ] Task: Live End-to-End Smoke Verification CLI
    - [ ] Implement `src/provisioning/verify_e2e.py` testing live BigQuery query, Discovery Engine search, and ADK invocation
    - [ ] Verify error handling and diagnostic reporting

- [ ] Task: Conductor - User Manual Verification 'Automated Verification Suite & Quality Gates' (Protocol in workflow.md)
