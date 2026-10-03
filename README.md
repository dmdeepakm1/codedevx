# CodeDevX

CodeDevX is a model-independent engineering knowledge and coding-agent platform for **multiple projects and multiple repositories**. Its purpose is to make distributed engineering knowledge searchable and usable across frontend, backend, shared libraries, infrastructure, architecture documents, runbooks, and eventually enterprise systems such as Confluence and Jira.

The core design principle is:

> **Organizational knowledge belongs in CodeDevX, not inside a particular LLM.**

This allows the same engineering context to be used by OpenAI, local Ollama models, and future Claude/Kiro/MCP-capable clients without rebuilding the knowledge base.

---

## Status: implemented vs target architecture

This repository is a **working production-oriented baseline under active development**. Do not interpret the V1/V2/V3 names as a claim that every target capability is already production-certified.

### Implemented now

- Multi-project registration
- Multiple Git repositories per project
- Repository types: frontend, backend, shared, infra, unknown
- PostgreSQL project/repository/index state
- Incremental indexing using Git SHAs and changed files
- Deterministic source chunking
- Content hashing to avoid re-embedding unchanged chunks
- Qdrant vector storage and project-scoped semantic retrieval
- OpenAI embeddings and reasoning provider
- Markdown/ADR/runbook knowledge ingestion into Qdrant
- V1/V2/V3 runtime profile flag
- V2 hybrid retrieval interface
- Neo4j graph-store adapter and graph lookup
- Ollama local LLM provider
- MCP server exposing CodeDevX engineering retrieval
- V3 workspace-contained file read/write primitives
- V3 allow-listed build/test command execution
- Podman-compatible PostgreSQL + Qdrant + Neo4j local infrastructure

### Partially implemented

- **Graph RAG:** Neo4j storage/query infrastructure exists, but the source indexer does not yet build a complete AST/call/dependency graph.
- **Hybrid RAG:** vector + optional graph retrieval exists; advanced reranking, lexical/BM25 retrieval and reciprocal-rank fusion are future improvements.
- **V3 coding agent:** safe workspace primitives exist, but the complete plan → edit → build → test → diagnose → repair loop is not implemented yet.
- **Knowledge ingestion:** Markdown is implemented. Enterprise Confluence/Jira authentication and synchronization are not.
- **Incremental indexing:** changed files/chunks are handled; complete deleted-file/vector/graph reconciliation still needs to be added.

### Not implemented yet

- Tree-sitter AST extraction
- Joern/CPG deep program analysis
- Complete cross-repository dependency graph
- Automatic frontend → API → backend → DB/event tracing
- Confluence authenticated connector
- Jira authenticated connector
- GitHub/GitLab webhook indexing
- Claude provider
- Direct llama.cpp provider
- Claude Code/Kiro client-specific configuration
- PR review agent
- production support/incident agent
- autonomous impact-analysis agent
- full V3 self-correcting coding loop
- enterprise RBAC/SSO, HA, centralized secrets, telemetry and backup policies

These are extension points, not capabilities that this README claims already work.

---

## Architecture guides

- [AI-DLC integration](docs/AIDLC_INTEGRATION.md) — how CodeDevX supplies engineering context to a spec-driven AI-DLC workflow.
- [Multi-team / multi-project architecture](docs/MULTI_TEAM_MULTI_PROJECT_ARCHITECTURE.md) — target workspace, team, project-area, repository-membership and shared-repository model.
- [Integrated AI-DLC + MCP architecture](docs/INTEGRATION_ARCHITECTURE.md) — provenance-aware relationships, human approval boundaries and external Jira/Confluence MCP integration.
- [Local setup — V1, V2 and V3](docs/LOCAL_SETUP_V1_V2_V3.md) — prerequisites, installation, configuration and smoke tests.
- [Jira → Design → Code workflow](docs/JIRA_TO_DESIGN_TO_CODE_WORKFLOW.md) — reverse engineering, HLD/LLD, human approval gates and implementation flow.

# Architecture

## Target platform architecture

```text
                         ┌──────────────────────────┐
                         │        CodeDevX          │
                         │ Engineering Intelligence │
                         └────────────┬─────────────┘
                                      │
             ┌────────────────────────┼─────────────────────────┐
             │                        │                         │
             ▼                        ▼                         ▼
      SOURCE CODE                KNOWLEDGE                 WORK ITEMS
   ┌───────────────┐       ┌────────────────┐        ┌────────────────┐
   │ Frontend repos│       │ Markdown / ADR │        │ Jira (future)  │
   │ Backend repos │       │ Runbooks       │        │ Bugs/incidents │
   │ Shared repos  │       │ Confluence (*) │        │ Support cases  │
   │ Infra repos   │       │ Design docs    │        │                │
   └───────┬───────┘       └────────┬───────┘        └────────┬───────┘
           │                        │                         │
           └────────────────────────┼─────────────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   INGESTION LAYER    │
                         │ Git diff / chunking  │
                         │ metadata / adapters  │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    ▼                                ▼
             ┌─────────────┐                  ┌─────────────┐
             │   Qdrant    │                  │    Neo4j    │
             │ Vector RAG  │                  │ Graph RAG   │
             └──────┬──────┘                  └──────┬──────┘
                    │                                │
                    └───────────────┬────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  HYBRID RETRIEVER    │
                         │ vector + graph       │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   CONTEXT BUILDER    │
                         │ project scoped       │
                         │ token bounded        │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │    MODEL ROUTER      │
                         └─────┬────────┬───────┘
                               │        │
                         ┌─────▼───┐ ┌──▼──────┐
                         │ OpenAI  │ │ Ollama  │
                         └─────────┘ └─────────┘
                               Future adapters:
                           Claude / llama.cpp / others
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      MCP SERVER      │
                         │ shared knowledge API │
                         └──────────┬───────────┘
                                    │
                         Future MCP-capable clients
                         Claude / Kiro / IDE agents
```

(*) Confluence and Jira are target enterprise adapters; they are **not currently implemented**.

## Intended cross-repository knowledge graph

The future AST/graph index should represent relationships such as:

```text
React / Angular Component
          │
          ▼
Frontend API Client
          │ CALLS_API
          ▼
      /api/products/{id}
          │
          ▼
Spring/.NET/Node Controller
          │ CALLS
          ▼
       Service
          │
          ▼
      Repository
          │
          ▼
 PostgreSQL / Event / Kafka
```

Target graph entities include:

```text
Project
Repository
Module / Package
Class / Interface
Method / Function
UI Component
API Endpoint
Database Table
Kafka Topic / Event
Configuration
Test
Service
Domain Concept
Jira Item
Confluence Page
```

Target relationships include:

```text
CONTAINS
IMPORTS
CALLS
IMPLEMENTS
EXTENDS
DEPENDS_ON
EXPOSES_API
CALLS_API
READS_FROM
WRITES_TO
PUBLISHES_EVENT
CONSUMES_EVENT
TESTED_BY
DOCUMENTED_BY
RELATED_TO_JIRA
```

The Neo4j adapter exists today, but complete extraction of these relationships requires the planned Tree-sitter/Joern work.

---

# V1 → V2 → V3

Set the active profile using:

```bash
CODEDEVX_VERSION=1
```

Profiles are additive. V3 reuses the same project state, Qdrant knowledge and graph infrastructure created by earlier profiles.

## V1 — Code Intelligence

```text
Git repositories
      │
      ▼
Git SHA / diff
      │
      ▼
Deterministic code chunks
      │
      ▼
Content hash
      │
      ├──── unchanged → skip
      │
      ▼ changed
OpenAI embeddings
      │
      ▼
Qdrant
      │
      ▼
Project-scoped Code RAG
      │
      ▼
OpenAI
```

Use V1 to validate multi-repository indexing and code Q&A.

## V2 — Engineering Knowledge + Hybrid RAG

```text
             Code repositories
                    │
                    ├──────────────┐
                    │              │
             Markdown / ADRs    Neo4j (*)
             Runbooks/docs         │
                    │              │
                    ▼              ▼
                 Qdrant        Graph lookup
                    │              │
                    └──────┬───────┘
                           ▼
                    Hybrid Retriever
                           │
                           ▼
                    Context Builder
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                 OpenAI         Ollama
```

(*) Graph retrieval is implemented, but complete code-relationship population is still planned.

## V3 — Agentic Engineering

V3 is intended to evolve V2 into:

```text
                    Engineering request
                           │
                           ▼
                     Domain context
                           │
                    Hybrid RAG / MCP
                           │
                           ▼
                         Plan
                           │
                           ▼
                       Read code
                           │
                           ▼
                       Edit code
                           │
                           ▼
                     Build / Test
                           │
                  ┌────────┴────────┐
                  │ pass            │ fail
                  ▼                 ▼
              Final diff      Diagnose failure
                                    │
                                    ▼
                                  Repair
                                    │
                                    └──→ Build/Test
```

Today, workspace-contained read/write and allow-listed command execution are implemented. The autonomous loop above is a **target V3 capability**, not yet complete.

---

# Why both Vector RAG and Graph RAG?

Vector retrieval is useful for questions such as:

- "Where is phone-number validation handled?"
- "Find documentation describing merge behavior."
- "Which code looks related to canonical record processing?"

Graph retrieval becomes important for questions such as:

- "What calls this API?"
- "Which frontend component depends on this backend endpoint?"
- "If this service changes, which repositories and tests are affected?"
- "Trace this flow from UI to database."

The intended retrieval pipeline is:

```text
Question
   │
   ├── Vector retrieval ───── Qdrant
   │
   ├── Graph traversal ────── Neo4j
   │
   ├── Keyword retrieval ──── future
   │
   └── Enterprise knowledge ─ future Confluence/Jira adapters
                 │
                 ▼
          Ranking / filtering
                 │
                 ▼
          Token-bounded context
                 │
                 ▼
             LLM provider
```

The goal is to avoid sending entire repositories to an LLM. Deterministic retrieval narrows the evidence first.

---

# Model independence

Do **not** create separate organizational knowledge stores for each model.

```text
              CodeDevX Knowledge
             ┌────────┴────────┐
             ▼                 ▼
          Qdrant             Neo4j
             └────────┬────────┘
                      ▼
                Hybrid RAG
                      ▼
                 Model Router
            ┌─────────┼─────────┐
            ▼         ▼         ▼
         OpenAI     Ollama    future
                            Claude/llama.cpp
```

This allows a task to use local Ollama when appropriate and another provider for deeper reasoning without rebuilding the knowledge base.

---

# AI-DLC harness integration

For structured delivery workflows, use AI-DLC as the harness-neutral lifecycle engine and CodeDevX as the engineering-evidence layer. AI-DLC already supports Claude Code, Kiro CLI/IDE, Codex, Cursor, opencode and GitHub Copilot through thin harness integrations. Configure the harness with AI-DLC, then expose CodeDevX MCP to that harness.

```text
AI-DLC harness
   │
   ├── workflow/gates/state
   ▼
CodeDevX MCP
   └── code + knowledge evidence
```

Do not duplicate provider/model or harness setup inside CodeDevX. See `docs/EXTERNAL_AGENT_MCP.md`.

# MCP architecture

CodeDevX includes an MCP server entry point:

```bash
codedevx-mcp
```

The server exposes:

```text
search_engineering_knowledge(project_id, query, limit)
```

Intended integration:

```text
Claude / Kiro / IDE Agent
          │
          │ MCP
          ▼
   CodeDevX MCP Server
          │
          ▼
    Hybrid Retriever
       │       │
       ▼       ▼
    Qdrant   Neo4j
```

Keep client-specific Claude/Kiro configuration outside the core knowledge architecture. MCP is the interoperability boundary. Client authentication and exact configuration must be validated against the specific client/version before use.

---

# Local installation — macOS + Podman

## Prerequisites

Install:

- Git
- Python 3.11 or newer
- Podman Desktop or Podman CLI
- Ollama only if you want local inference

Clone and install:

```bash
git clone https://github.com/dmdeepakm1/codedevx.git
cd codedevx

python3.11 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

cp .env.example .env

podman compose up -d
```

Local infrastructure:

| Service | Purpose | Port |
|---|---|---:|
| PostgreSQL | project/repository/index state | 5432 |
| Qdrant | vector knowledge | 6333/6334 |
| Neo4j | graph knowledge | 7474/7687 |

The credentials in `compose.yaml` are **local-development defaults only**.

---

# Configuration

Important `.env` values:

```bash
OPENAI_API_KEY=

CODEDEVX_VERSION=1

CODEDEVX_OPENAI_MODEL=gpt-5.6
CODEDEVX_EMBEDDING_MODEL=text-embedding-3-small

CODEDEVX_POSTGRES_URL=postgresql+psycopg://codedevx:codedevx@localhost:5432/codedevx

CODEDEVX_QDRANT_URL=http://localhost:6333
CODEDEVX_QDRANT_COLLECTION=codedevx_code
CODEDEVX_MAX_CONTEXT_CHUNKS=12

CODEDEVX_GRAPH_ENABLED=false
CODEDEVX_STRICT_INTEGRATIONS=false

CODEDEVX_NEO4J_URI=bolt://localhost:7687
CODEDEVX_NEO4J_USER=neo4j
CODEDEVX_NEO4J_PASSWORD=codedevx-local
CODEDEVX_NEO4J_DATABASE=neo4j

CODEDEVX_OLLAMA_URL=http://localhost:11434
CODEDEVX_OLLAMA_MODEL=qwen3-coder
CODEDEVX_LLM_TIMEOUT_SECONDS=180
```

Never commit your real `.env`.

---

# Running V1

Register a project:

```bash
codedevx project-add commerce-platform
```

Register multiple repositories:

```bash
codedevx repo-add commerce-platform frontend /absolute/path/frontend frontend
codedevx repo-add commerce-platform backend /absolute/path/backend backend
codedevx repo-add commerce-platform shared /absolute/path/shared shared
```

Index:

```bash
codedevx index commerce-platform
```

Ask:

```bash
codedevx ask commerce-platform "Where is product validation implemented?"
```

---

# Running V2

Set:

```bash
CODEDEVX_VERSION=2
```

For optional graph retrieval:

```bash
CODEDEVX_GRAPH_ENABLED=true
```

Add Markdown knowledge:

```bash
codedevx knowledge-add commerce-platform /absolute/path/to/knowledge
```

This directory can contain exported architecture notes, ADRs, runbooks and other Markdown documentation.

Ask using OpenAI:

```bash
codedevx ask commerce-platform "Explain the design and show the relevant code"
```

Ask using Ollama:

```bash
codedevx ask commerce-platform "Explain the design and show the relevant code" --provider ollama
```

Before using Ollama, install/start Ollama separately and pull a model available in your Ollama installation. Set `CODEDEVX_OLLAMA_MODEL` to the exact installed model identifier.

---

# Incremental indexing

CodeDevX stores the last indexed Git SHA for every repository.

```text
Previous SHA
     │
     ▼
git diff previous..current
     │
     ▼
Changed files
     │
     ▼
Analyze changed content
     │
     ▼
Content hash
     │
 ┌───┴────────┐
 │ unchanged  │ changed
 ▼            ▼
skip       re-embed
               │
               ▼
             Qdrant
```

This avoids reprocessing the entire project after every commit.

**Known gap:** complete removal of vectors/graph nodes for deleted or renamed source files is not yet implemented.

---

# Multi-project isolation

Identifiers include project and repository scope.

```text
Project A
 ├── frontend
 ├── backend
 └── shared

Project B
 ├── web
 ├── api
 └── infrastructure
```

Vector retrieval applies a `project_id` filter so one project's code is not intentionally mixed into another project's RAG context.

---

# Safety model for V3

The current workspace utility:

- resolves files beneath a configured workspace root
- rejects path traversal outside that root
- supports controlled file reads/writes
- runs only allow-listed executable names
- applies command timeouts
- captures bounded command output

Current executable allow list includes common development commands such as Python/pytest, Maven/Gradle, npm/pnpm/yarn and Git.

This is a baseline—not a complete sandbox. For serious agentic coding:

1. use disposable Git branches/worktrees;
2. use containers/isolated CI workers;
3. do not expose production credentials;
4. require review before merge/deployment;
5. restrict network and filesystem access;
6. log tool calls and resulting diffs.

---

# Planned production roadmap

## Next — finish V2

1. Tree-sitter parsers per supported language.
2. Symbol-level AST extraction.
3. IMPORTS/CALLS/IMPLEMENTS/EXTENDS relationships.
4. API endpoint extraction.
5. Frontend API-client → backend endpoint linking.
6. DB/event/topic relationship extraction.
7. Graph delta updates.
8. Deleted/renamed-file reconciliation.
9. lexical + vector + graph ranking.
10. authenticated Confluence/Jira adapters or organization-approved MCP connectors.

## Then — finish V3

1. task planner;
2. repository/tool selection;
3. impact analysis;
4. controlled file edits;
5. build/test execution;
6. failure diagnosis;
7. bounded self-correction loop;
8. final diff/explanation;
9. PR-review agent;
10. support/troubleshooting agent;
11. architecture/domain-expert agent.

## Later

- Joern/CPG for deeper static analysis
- GitHub/GitLab webhook incremental indexing
- direct llama.cpp provider if required
- additional LLM providers
- CI indexing
- observability/metrics/tracing
- RBAC/SSO
- secrets manager
- HA/backup/restore
- evaluation/golden datasets for retrieval and agent quality

---

# Future domain-expert use case

The long-term system should be able to answer questions such as:

```text
"How does Record Management merge work?"

"Which repositories implement this capability?"

"Show the architecture documentation explaining why it works this way."

"What calls this endpoint?"

"If I change this DTO, what frontend/backend/tests are impacted?"

"Find previous incidents related to this failure."

"Implement this Jira requirement, run the tests and show me the final diff."
```

The first questions are primarily knowledge/RAG problems. The last one requires the completed V3 agent loop.

---

# Repository structure

```text
src/codedevx/
├── analyzers/       deterministic source analysis
├── graph/           Neo4j graph adapter
├── knowledge/       document knowledge adapters
├── llm/             model-provider abstraction
├── mcp/             MCP knowledge server
├── retrieval/       hybrid retrieval
├── storage/         PostgreSQL state
├── tools/           guarded V3 workspace tools
├── vector/          Qdrant vector store
├── agent.py         engineering Q&A orchestration
├── cli.py           CLI commands
├── config.py        runtime configuration
├── domain.py        core domain objects
├── git.py           Git incremental-index helpers
├── indexer.py       project/repository indexing
└── profiles.py      V1/V2/V3 profile definitions
```

---

# Extension rules

When adding a capability, keep it behind an interface instead of coupling the platform to one vendor.

Examples:

```text
LLMProvider
 ├── OpenAIProvider
 ├── OllamaProvider
 ├── ClaudeProvider       future
 └── LlamaCppProvider     future

KnowledgeAdapter
 ├── Markdown
 ├── Confluence           future
 └── Jira                 future

Retrieval
 ├── Vector / Qdrant
 ├── Graph / Neo4j
 └── Lexical              future
```

This is what allows CodeDevX to evolve without rebuilding its organizational knowledge every time the model or coding client changes.

---

# Production checklist before organizational deployment

The local POC can run before these are complete, but a shared enterprise deployment should add:

- pinned/tested dependency lock file
- automated unit/integration tests
- CI quality gates
- secret manager integration
- TLS for data services
- authenticated Qdrant/Neo4j/PostgreSQL
- RBAC
- audit logging
- structured application logging
- metrics/tracing
- backup/restore procedures
- retention/deletion policies
- connector rate limiting/retry policies
- enterprise data classification controls
- prompt-injection/content-trust controls for retrieved documents
- retrieval quality evaluation
- agent action policies and human approval boundaries

---

# Security

Never commit:

- `.env`
- OpenAI/Anthropic API keys
- Jira/Confluence tokens
- GitHub tokens
- database production passwords
- customer/internal proprietary exports intended to remain local

The repository's default credentials and compose configuration are intended for **local development only**.

---

# Current verification note

This README was updated against the current files in the GitHub repository, including the active configuration, dependencies, V1/V2/V3 profile logic, hybrid retriever, Neo4j adapter, Markdown knowledge ingestion, Ollama provider, MCP server and V3 workspace tools.

It intentionally separates **implemented**, **partial**, and **planned** capabilities so future work is not mistaken for working functionality.

## V1 repository discovery and context budget

Repository language, framework and build information is detected from tracked source files and build manifests during `codedevx index`. The profile is stored in PostgreSQL and shown in index output or with `codedevx repo-profile PROJECT_ID`. Detection is heuristic; a Java build file alone does not establish every framework in use.

An optional `codedevx.spec.md` at each repository root can add hints, exclude paths and narrative architecture context. Copy [`codedevx.example.spec.md`](codedevx.example.spec.md) and edit it for that repository. The `## CodeDevX metadata` section uses simple `- Field: value` lines; commas separate multiple values. Hints supplement detection; mismatches appear as warnings, so they are not silently treated as facts. Untracked files are not discovered by the Git indexer. Commit spec edits before reindexing; the spec is re-read on every `index` call even without a source SHA change.

`CODEDEVX_MAX_CONTEXT_TOKENS` defaults to 20000, and `CODEDEVX_MAX_CONTEXT_CHUNKS` defaults to 24. The V1 context builder ranks retrieved chunks by similarity, keeps file and line citations, and allocates estimated tokens to architecture knowledge, source and tests. It does not send the whole repository to the model. The token estimate is conservative and provider-neutral, not an exact billing count. Retrieved code is line chunked and semantic; this version does not prove complete cross-repository call tracing. A large requirement is rejected when it exceeds its reserved budget.
