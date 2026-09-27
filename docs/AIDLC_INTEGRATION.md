# CodeDevX + AI-DLC Integration Guide

## Purpose

This document describes how **CodeDevX can be used as the engineering knowledge and context layer for an AI-Driven Development Lifecycle (AI-DLC)**.

CodeDevX should **not replace the AI-DLC workflow**. The AI-DLC workflow remains responsible for lifecycle orchestration, stages, artifacts, approvals and development process. CodeDevX provides grounded engineering context from code and organizational knowledge.

The intended separation is:

```text
AI-DLC = process / workflow / lifecycle orchestration

CodeDevX = engineering knowledge / retrieval / context / impact intelligence

Claude / Kiro / other agent = reasoning and generation
```

---

# High-level architecture

```text
                         AI-DLC WORKFLOW
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
        INCEPTION         CONSTRUCTION        OPERATIONS
       Requirements       HLD / LLD            Support
       Acceptance         Implementation       Incidents
       Architecture       Unit tests           Troubleshooting
            │             Integration tests         │
            │             Code review               │
            └──────────────────┼─────────────────────┘
                               │
                               ▼
                    CodeDevX Context Layer
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
      SOURCE CODE          KNOWLEDGE             WORK ITEMS
   Frontend/backend      ADRs / Runbooks       Jira (future)
   Shared/infra repos    Markdown/docs         Incidents
          │              Confluence (*)        Support cases
          └────────────────────┼────────────────────┘
                               ▼
                       INGESTION / INDEXING
                               │
                   ┌───────────┴───────────┐
                   ▼                       ▼
                Qdrant                   Neo4j
              Vector RAG               Graph RAG
                   └───────────┬───────────┘
                               ▼
                        Hybrid Retriever
                               │
                               ▼
                         Context Builder
                               │
                               ▼
                         CodeDevX MCP
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
           Claude            Kiro          Other Agents
```

(*) Confluence/Jira enterprise connectors are target capabilities and are not currently implemented in CodeDevX.

---

# Why CodeDevX is useful for AI-DLC

A lifecycle agent should not generate engineering artifacts using only the requirement supplied in the current prompt.

For example, before generating an HLD or LLD it may need to understand:

- existing services and repositories;
- frontend/backend boundaries;
- APIs already available;
- database and event dependencies;
- shared frameworks;
- existing architecture decisions;
- similar implementations;
- relevant tests;
- operational constraints;
- previous incidents;
- related requirements.

CodeDevX is intended to provide that context.

```text
Requirement
    │
    ▼
AI-DLC stage
    │
    ▼
"What engineering context do I need?"
    │
    ▼
CodeDevX MCP / Retrieval
    │
    ├── Code
    ├── Architecture
    ├── ADRs
    ├── Runbooks
    ├── Graph relationships
    ├── Jira              future
    └── Confluence        future
    │
    ▼
Grounded context
    │
    ▼
Claude / Kiro / LLM
    │
    ▼
AI-DLC artifact
```

---

# AI-DLC lifecycle integration

## 1. Requirement / Inception

Example input:

```text
Add phone-number validation to the customer product experience.
```

Before creating architecture or implementation artifacts, AI-DLC could query CodeDevX:

```text
Which repositories contain phone/customer validation?

Is there an existing validation framework?

Which frontend component captures the phone number?

Which backend API receives it?

Are there existing validation services?

What tests cover this behavior?

Are there architecture documents describing validation?
```

Expected output from CodeDevX is **evidence**, not a generated design.

AI-DLC can then use that evidence to construct requirements and design artifacts.

---

# 2. Impact Analysis

Target flow:

```text
Requirement
    │
    ▼
Requirement Analyzer
    │
    ▼
CodeDevX Hybrid RAG
    │
    ├── Vector similarity
    ├── Graph dependencies
    └── Domain knowledge
    │
    ▼
Potential impact
    │
    ├── Repository A
    ├── Repository B
    ├── API endpoint
    ├── Component
    ├── Service
    ├── Database/event
    └── Tests
```

This becomes substantially more accurate once the planned Tree-sitter dependency graph is implemented.

---

# 3. HLD Generation

The HLD agent should retrieve:

```text
Requirement
+
Existing architecture
+
Related services
+
Current API boundaries
+
Architecture decisions
+
Cross-repository dependencies
+
Platform constraints
```

Then generate:

```text
HLD
├── Context
├── Current architecture
├── Proposed architecture
├── Components affected
├── APIs/events
├── Data flow
├── Security
├── Scalability
├── Dependencies
├── Risks
└── Alternatives
```

The LLM should not invent existing components. Existing-system statements should be grounded in CodeDevX evidence.

---

# 4. LLD Generation

The LLD stage needs deeper source context:

```text
HLD
 +
CodeDevX
   ├── Classes
   ├── Interfaces
   ├── Methods
   ├── APIs
   ├── DTOs
   ├── schemas
   ├── repositories
   └── tests
        │
        ▼
       LLD
```

Potential LLD sections:

```text
Classes/modules to modify
New classes/modules
Interfaces
Method signatures
API changes
Data-model changes
Validation rules
Error handling
Configuration
Logging
Test strategy
Migration/compatibility
```

Tree-sitter/Joern will eventually improve the structural accuracy of this stage.

---

# 5. Implementation Planning

AI-DLC can transform the HLD/LLD into a grounded implementation plan.

Example:

```text
Implementation Plan

1. frontend repo
   - update PhoneEditor component
   - update API payload handling
   - add component tests

2. backend repo
   - update validation service
   - add validation error mapping
   - add unit tests

3. shared repo
   - update common validation model

4. integration tests
   - valid number
   - invalid number
   - missing country code
```

Actual file/class names must come from retrieval rather than assumptions.

---

# 6. Coding Agent

Target V3 integration:

```text
Implementation task
       │
       ▼
AI-DLC
       │
       ▼
CodeDevX context
       │
       ▼
Coding Agent
       │
       ├── Read
       ├── Search
       ├── Edit
       ├── Build
       └── Test
             │
       ┌─────┴─────┐
       ▼           ▼
     PASS         FAIL
       │           │
       │        Diagnose
       │           │
       │         Repair
       │           │
       └───────────┘
             │
             ▼
          Git diff
```

CodeDevX currently contains guarded workspace primitives, but the complete autonomous loop is a planned V3 capability.

---

# 7. Test Generation

AI-DLC can ask CodeDevX for:

```text
existing tests
testing frameworks
affected methods
API contracts
edge cases from documentation
previous bugs/incidents
acceptance criteria
```

Then generate:

```text
Unit tests
Integration tests
Contract tests
UI tests
Regression tests
Negative tests
```

This is preferable to asking an LLM to create tests without understanding the repository's existing testing conventions.

---

# 8. Review

Target review context:

```text
Requirement
+
HLD
+
LLD
+
Implementation plan
+
Git diff
+
Existing architecture
+
Test results
        │
        ▼
   AI Review Agent
```

Review findings can include:

- requirement coverage;
- architecture deviations;
- missing tests;
- unintended cross-repository impact;
- compatibility risks;
- documentation drift.

A PR-review agent is not currently implemented.

---

# 9. Operations / Support

The same engineering knowledge should be reusable after development.

```text
Production issue
      │
      ▼
Support Agent
      │
      ▼
CodeDevX
 ├── Source code
 ├── architecture
 ├── runbooks
 ├── dependencies
 ├── previous incidents   future
 └── Jira/support         future
      │
      ▼
Probable investigation paths
```

This avoids creating a separate knowledge platform for development and production support.

---

# Proposed AI-DLC package

The recommended future CodeDevX package is:

```text
src/codedevx/aidlc/
├── __init__.py
├── artifact_types.py
├── adapter.py
├── context_builder.py
├── requirement_analyzer.py
├── impact_analyzer.py
├── hld_context.py
├── lld_context.py
├── test_context.py
└── implementation_context.py
```

Responsibilities:

| Module | Responsibility |
|---|---|
| artifact_types | AI-DLC artifact/stage definitions |
| adapter | boundary between AI-DLC workflow and CodeDevX |
| context_builder | retrieve and budget engineering context |
| requirement_analyzer | identify concepts/repos/domains from requirements |
| impact_analyzer | determine likely affected engineering areas |
| hld_context | architecture-focused retrieval |
| lld_context | symbol/source-focused retrieval |
| test_context | test and acceptance-criteria retrieval |
| implementation_context | context for coding agents |

This package is **proposed architecture** and is not currently present in the repository.

---

# Artifact model

A future artifact model could represent:

```text
Requirement
   │
   ├── Acceptance Criteria
   │
   ▼
Impact Analysis
   │
   ▼
HLD
   │
   ▼
LLD
   │
   ▼
Implementation Plan
   │
   ▼
Code Change
   │
   ▼
Test Plan / Test Results
   │
   ▼
Review
```

Each artifact should retain:

- project ID;
- source requirement/work-item ID;
- lifecycle stage;
- source references;
- repository references;
- generated timestamp;
- model/provider metadata;
- artifact version;
- approval state.

The generated artifact should be traceable back to its evidence.

---

# MCP as the integration boundary

Recommended approach:

```text
AI-DLC / Claude / Kiro
          │
          │ MCP
          ▼
    CodeDevX MCP
          │
          ▼
 Hybrid Retriever
   │           │
   ▼           ▼
Qdrant       Neo4j
```

CodeDevX currently exposes:

```text
search_engineering_knowledge(project_id, query, limit)
```

Future AI-DLC-oriented MCP tools could include:

```text
analyze_requirement
find_affected_repositories
get_architecture_context
get_hld_context
get_lld_context
get_test_context
trace_dependency
find_related_incidents
prepare_implementation_context
```

These should be implemented only when the underlying retrieval capability exists. Tool names in this section are proposed, not current MCP APIs.

---

# AI-DLC + model routing

Keep the workflow independent of a particular model.

```text
                  AI-DLC
                     │
                     ▼
                  CodeDevX
                     │
                     ▼
                Model Router
           ┌─────────┼─────────┐
           ▼         ▼         ▼
        OpenAI     Ollama    Future
                           Claude/other
```

Example routing policy:

```text
Local/private/simple analysis
        → Ollama

Deep architecture/reasoning
        → approved hosted provider

Provider unavailable/quota exhausted
        → configured fallback
```

The task state and engineering knowledge should remain outside the model so changing providers does not require restarting the lifecycle.

---

# Recommended adoption sequence

## Phase 1 — current CodeDevX

Validate:

- multiple repositories;
- incremental indexing;
- code RAG;
- project isolation;
- Markdown knowledge;
- OpenAI/Ollama.

## Phase 2 — finish engineering knowledge

Add:

- Tree-sitter;
- source relationships;
- full graph population;
- deleted-file reconciliation;
- hybrid ranking;
- Confluence/Jira or approved MCP enterprise connectors.

## Phase 3 — AI-DLC adapter

Add:

- lifecycle artifact types;
- requirement context;
- impact analysis;
- HLD context;
- LLD context;
- test context;
- artifact provenance.

## Phase 4 — agentic implementation

Add:

- implementation planning;
- controlled editing;
- build/test;
- bounded self-correction;
- diff generation;
- review workflow.

## Phase 5 — operational intelligence

Add:

- incident knowledge;
- support troubleshooting;
- architecture drift detection;
- change-impact intelligence;
- knowledge freshness monitoring.

---

# Example end-to-end flow

```text
Jira Requirement
      │
      ▼
AI-DLC Inception
      │
      ▼
Requirement Analyzer
      │
      ▼
CodeDevX MCP
      │
      ├── existing code
      ├── architecture
      ├── related documentation
      └── dependency graph
      │
      ▼
Impact Analysis
      │
      ▼
HLD
      │
      ▼
LLD
      │
      ▼
Implementation Plan
      │
      ▼
Coding Agent
      │
      ├── edit
      ├── build
      ├── test
      └── repair
      │
      ▼
Review Agent
      │
      ▼
Pull Request
      │
      ▼
CI / Human Approval
```

Jira retrieval, the full coding loop and PR automation in this diagram are target capabilities.

---

# Important design principle

Avoid this:

```text
AI-DLC knowledge
Claude knowledge
Kiro knowledge
Support-agent knowledge
Coding-agent knowledge
```

Prefer:

```text
                 CodeDevX
          Engineering Knowledge
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     AI-DLC     Claude     Kiro
        │
        ├── Coding Agent
        ├── Domain Expert
        ├── Review Agent
        └── Support Agent
```

One governed knowledge platform should serve all of these consumers.

---

# Current conclusion

CodeDevX is suitable as the **knowledge/context foundation** for AI-DLC.

Today it can provide multi-repository code RAG, Markdown knowledge, project isolation, OpenAI/Ollama routing and an MCP retrieval interface.

It does **not yet provide a complete AI-DLC integration**. The dedicated AI-DLC adapter, lifecycle artifact/provenance model, complete source dependency graph, enterprise Jira/Confluence ingestion and V3 autonomous implementation loop remain future work.

This distinction is intentional so architecture plans are not confused with currently working functionality.
