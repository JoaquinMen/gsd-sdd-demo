# Implementation Plan: Safe Agent App (`safe_agent_app_20261023`)

This plan tracks the phased, test-driven implementation of the Safe Agent App conversational platform, following the Conductor workflow and strict safety guardrails.

---

## Phase 1: Environment Scaffolding & Configuration Bootstrap

- [ ] Task: Project Manifests & Configuration Templates
    - [ ] Create `pyproject.toml` and pinned `requirements.txt` with ADK, GenAI, and GCP dependencies
    - [ ] Create `.env.example` documenting all runtime and provisioning variables
    - [ ] Verify dependencies install cleanly into virtual environment

- [ ] Task: App Configuration & TLS/mTLS Bootstrap Engine
    - [ ] Write unit tests in `tests/test_config.py` verifying `AppConfig` parsing, validation, and SSL cert resolution
    - [ ] Implement `src/agent/config.py` with `AppConfig` dataclass and `_ensure_ssl_cert_file`
    - [ ] Run `pytest tests/test_config.py` and confirm all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Environment Scaffolding & Configuration Bootstrap' (Protocol in workflow.md)

---

## Phase 2: Automated Data Provisioning & Seeding Pipeline

- [ ] Task: Policy Document Synthesis Engine
    - [ ] Write unit test in `tests/test_document_generator.py` asserting PDF page structure and content clauses
    - [ ] Implement `src/provisioning/generate_documents.py` using `fpdf2` generating 3 policy PDFs
    - [ ] Run `pytest tests/test_document_generator.py` and confirm all tests pass

- [ ] Task: Unstructured Discovery Engine Pipeline
    - [ ] Write unit test in `tests/test_setup_discovery_engine.py` mocking GCS and Discovery Engine clients
    - [ ] Implement `src/provisioning/setup_discovery_engine.py` with idempotent bucket provisioning and `import_documents`
    - [ ] Run `pytest tests/test_setup_discovery_engine.py` and confirm all tests pass

- [ ] Task: Structured Warehouse Seeding Pipeline
    - [ ] Write unit test in `tests/test_seed_warehouse.py` asserting dynamic rolling dates and 13-column schema
    - [ ] Implement `src/provisioning/seed_warehouse.py` with `WRITE_TRUNCATE` load job and schema declaration
    - [ ] Run `pytest tests/test_seed_warehouse.py` and confirm all tests pass

- [ ] Task: Master Provisioning Orchestrator
    - [ ] Implement `src/provisioning/setup_all.py` coordinating PDF generation, search setup, and BQ seeding
    - [ ] Add CLI arguments for `--wait`, `--skip-pdfs`, `--skip-vertex-search`, and `--skip-bigquery`
    - [ ] Verify CLI compiles and renders `--help` documentation properly

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Automated Data Provisioning & Seeding Pipeline' (Protocol in workflow.md)

---

## Phase 3: Safe Agent Core Runtime & Multi-Tool Engine

- [ ] Task: Unstructured Search Tool with Coexistence Flag
    - [ ] Write unit test in `tests/test_agent_tools.py` verifying `VertexAiSearchTool` instantiation and `bypass_multi_tools_limit=True`
    - [ ] Implement `src/agent/tools/search_tool.py` referencing configured Discovery Engine datastore path
    - [ ] Run `pytest tests/test_agent_tools.py -k test_search_tool` and confirm test passes

- [ ] Task: Hardened Read-Only BigQuery Toolset
    - [ ] Write unit test in `tests/test_agent_tools.py` asserting `WriteMode.BLOCKED` rejects mutating queries
    - [ ] Implement `src/agent/tools/billing_tool.py` wrapping `BigQueryToolset` with ADC credentials
    - [ ] Run `pytest tests/test_agent_tools.py -k test_billing_tool` and confirm test passes

- [ ] Task: Grounded System Prompt & Guardrails
    - [ ] Write unit test verifying prompt contains table schema, column descriptions, and citation rules
    - [ ] Implement `src/agent/prompts.py` with `build_system_prompt()` injecting table schema and domain boundaries
    - [ ] Run `pytest tests/test_agent_router.py -k test_prompts` and confirm test passes

- [ ] Task: Root Router Agent Assembly & ADK Web Entrypoint
    - [ ] Write unit test in `tests/test_agent_router.py` asserting `LlmAgent` configuration and model location
    - [ ] Implement `src/agent/agent.py` configuring `LlmAgent` with `gemini-3.5-flash` (`location="global"`)
    - [ ] Export `root_agent` in `src/agent/__init__.py` for ADK Web discovery (`adk web .`)
    - [ ] Run `pytest tests/test_agent_router.py` and confirm all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Safe Agent Core Runtime & Multi-Tool Engine' (Protocol in workflow.md)

---

## Phase 4: Automated Verification Suite & Live Smoke Test

- [ ] Task: Comprehensive Mock Unit Test Suite
    - [ ] Implement `tests/conftest.py` with mock environments and patch fixtures
    - [ ] Execute `pytest -v tests/` and verify 100% test pass rate
    - [ ] Verify statement coverage exceeds 80% with coverage report

- [ ] Task: Live End-to-End Smoke Verification CLI
    - [ ] Implement `src/provisioning/verify_e2e.py` testing live BigQuery query, Discovery Engine search, and ADK invocation
    - [ ] Test error handling and report formatting

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Automated Verification Suite & Live Smoke Test' (Protocol in workflow.md)
