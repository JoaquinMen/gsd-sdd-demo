# Product Guidelines

## Tone & Voice
- **Professional & Objective**: Deliver clear, authoritative operational and analytical guidance.
- **Transparent & Grounded**: Always cite the exact source document, jurisdiction, or database table backing an answer. If an answer cannot be grounded in the indexed corpus, explicitly state the limitation without hallucination.
- **Concise & Actionable**: Provide structured answers, summary tables, and clear metrics rather than verbose prose.

## User Experience Principles
- **Zero Ambiguity**: Differentiate between client-billable hours and internal operational hours; specify currency (USD) and date ranges clearly.
- **Explainability**: For analytical queries, provide the aggregated metrics alongside the underlying criteria used (e.g., date window, project IDs).
- **Graceful Error Handling**: Clearly explain query validation failures or blocked write attempts without exposing internal system traces.

## Architectural & Design Consistency
- **Clean Boundaries**: Strict separation between the presentation tier (ADK Web), agent runtime tier, and Google Cloud data/search services.
- **Idempotency by Default**: All setup and provisioning operations must be safely re-executable without generating duplicate records or dangling cloud assets.
