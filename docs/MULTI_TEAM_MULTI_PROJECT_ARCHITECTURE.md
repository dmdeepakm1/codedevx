# Multi-Team, Multi-Project, Multi-Repository Architecture

## Goal

CodeDevX should scale beyond a single project with several repositories.

The target hierarchy is:

```text
Organization / Workspace
│
├── Team A
│   ├── Project Area A1
│   │   ├── web-app
│   │   ├── product-api
│   │   └── domain-library
│   │
│   └── Project Area A2
│       ├── admin-ui
│       └── workflow-service
│
├── Team B
│   └── Project Area B1
│       ├── ingestion-service
│       └── event-consumer
│
└── Shared Platform
    ├── shared-sdk
    ├── identity-library
    ├── event-contracts
    └── deployment-framework
```

A repository may be primarily owned by one team while being consumed by many project areas.

---

# Current implementation

The current CodeDevX data model supports:

```text
Project
   │
   ├── Repository
   ├── Repository
   └── Repository
```

A repository record contains:

- `project_id`
- `repo_id`
- local Git path
- repository kind

Qdrant retrieval is filtered by `project_id`.

This is enough for a POC involving multiple repositories inside one project.

It does **not yet model Team, Project Area, Workspace, repository ownership or cross-project sharing as first-class entities**.

---

# Recommended target model

```text
Workspace
   │
   ├── Team
   │    │
   │    ├── ProjectArea
   │    │      │
   │    │      ├── RepositoryMembership ──► Repository
   │    │      ├── RepositoryMembership ──► Repository
   │    │      └── RepositoryMembership ──► Shared Repository
   │    │
   │    └── ProjectArea
   │
   └── Team
        └── ProjectArea
```

Do not duplicate a shared repository for every project.

Instead:

```text
Repository
   id = shared-sdk

ProjectArea A ── USES ──► shared-sdk
ProjectArea B ── USES ──► shared-sdk
ProjectArea C ── USES ──► shared-sdk
```

This preserves one source of truth.

---

# Suggested entities

## Workspace

Represents an organization or bounded engineering workspace.

Example:

```text
engineering
```

## Team

Represents an engineering ownership group.

Examples:

```text
catalog-team
experience-team
platform-team
```

## ProjectArea

Represents a product/domain/project boundary.

Examples:

```text
commerce-platform
customer-portal
data-processing
```

## Repository

A physical Git repository.

Examples:

```text
web-app
catalog-api
shared-sdk
event-contracts
```

## RepositoryMembership

Connects a repository to a project area and describes its role.

Suggested fields:

```text
workspace_id
project_area_id
repository_id
role
ownership
criticality
```

Possible roles:

```text
frontend
backend
shared
infrastructure
contract
test
documentation
```

---

# Ownership should be separate from usage

A shared repository may have one owner and many consumers.

```text
shared-sdk
    │
    ├── OWNED_BY ──► platform-team
    │
    ├── USED_BY ───► commerce-platform
    │
    ├── USED_BY ───► customer-portal
    │
    └── USED_BY ───► data-processing
```

This is more accurate than assigning the repository to a single project.

---

# Cross-repository relationships

The graph layer should connect symbols across repositories.

Example:

```text
web-app
 ProductPage
     │
     │ CALLS_API
     ▼
 /api/products/{id}
     │
     │ IMPLEMENTED_BY
     ▼
catalog-api
 ProductController
     │
     │ CALLS
     ▼
 ProductService
     │
     │ IMPORTS
     ▼
shared-domain
 ProductModel
```

This allows CodeDevX to answer:

```text
Which repositories participate in this feature?

What backend endpoint does this UI call?

Which projects consume this shared contract?

If shared-sdk changes, which project areas are affected?
```

---

# Cross-project relationships

Some dependencies cross project-area boundaries.

```text
Project Area A
     │
     │ CONSUMES_EVENT
     ▼
product.updated
     │
     │ CONSUMED_BY
     ▼
Project Area B
```

or:

```text
Project Area A
     │
     │ CALLS_API
     ▼
Project Area B / pricing-api
```

Neo4j is the appropriate layer for representing these relationships.

---

# Retrieval scope

Queries should have explicit scope.

## Repository scope

```text
workspace + project area + repository
```

Use when investigating one repository.

## Project-area scope

```text
workspace + project area
```

Search all repositories and knowledge belonging to that project area.

## Team scope

```text
workspace + team
```

Useful for architecture/support questions owned by a team.

## Workspace scope

```text
workspace
```

Useful for cross-project impact analysis.

Workspace-wide queries should normally be intentional rather than the default because they can increase noise, latency and token usage.

---

# Recommended Qdrant metadata

Future vector payloads should contain:

```json
{
  "workspace_id": "engineering",
  "team_id": "catalog-team",
  "project_area_ids": ["commerce-platform"],
  "repository_id": "catalog-api",
  "source_type": "code",
  "language": "java",
  "path": "src/...",
  "symbol": "ProductService"
}
```

A shared repository can contain multiple `project_area_ids`.

This enables filtered retrieval without creating duplicate embeddings.

---

# Recommended graph model

```text
(:Workspace)
(:Team)
(:ProjectArea)
(:Repository)
(:Module)
(:Class)
(:Method)
(:ApiEndpoint)
(:DatabaseTable)
(:Event)
(:Test)
(:Document)
(:WorkItem)
```

Relationships:

```text
WORKSPACE_HAS_TEAM
TEAM_OWNS_PROJECT
TEAM_OWNS_REPOSITORY
PROJECT_USES_REPOSITORY
CONTAINS
IMPORTS
CALLS
EXPOSES_API
CALLS_API
READS_FROM
WRITES_TO
PUBLISHES_EVENT
CONSUMES_EVENT
TESTED_BY
DOCUMENTED_BY
RELATED_TO_WORK_ITEM
DEPENDS_ON
```

---

# Shared repository indexing

Index each physical Git repository once.

Avoid:

```text
Project A → embed shared-sdk
Project B → embed shared-sdk again
Project C → embed shared-sdk again
```

Prefer:

```text
                    shared-sdk
                        │
                  index once
                        │
                 Qdrant / Neo4j
                  ▲      ▲      ▲
                  │      │      │
             Project A Project B Project C
```

Membership metadata determines which scopes can retrieve it.

Benefits:

- less storage;
- fewer embedding calls;
- consistent knowledge;
- simpler incremental updates;
- easier impact analysis.

---

# Incremental updates across shared repositories

```text
shared-sdk commit
       │
       ▼
Git diff
       │
       ▼
Changed symbols
       │
       ▼
Update vector + graph
       │
       ▼
Graph traversal
       │
       ├── Project A affected
       ├── Project B affected
       └── Project C affected
```

This becomes the basis for cross-team impact analysis.

---

# Suggested configuration

A future declarative configuration could look like:

```yaml
workspace: engineering

teams:
  - id: experience-team
    projects:
      - id: commerce-platform
        repositories:
          - id: web-app
            role: frontend
          - id: catalog-api
            role: backend
          - id: shared-sdk
            role: shared

  - id: operations-team
    projects:
      - id: order-processing
        repositories:
          - id: order-service
            role: backend
          - id: shared-sdk
            role: shared

repositories:
  shared-sdk:
    owner: platform-team
```

This configuration format is **proposed**; it is not currently implemented.

---

# AI-DLC implications

The hierarchy improves AI-DLC context selection.

For a requirement associated with `commerce-platform`:

```text
Requirement
    │
    ▼
Project Area
    │
    ├── directly owned repositories
    ├── shared repositories
    ├── graph dependencies
    └── related architecture
    │
    ▼
AI-DLC context
```

For impact analysis, CodeDevX can deliberately expand beyond the project:

```text
Changed shared symbol
      │
      ▼
Graph traversal
      │
      ├── commerce-platform
      ├── order-processing
      └── reporting-platform
```

That prevents AI-DLC from producing a design based only on the repository in which the requirement was initially raised.

---

# Recommended implementation order

## Step 1

Keep the existing `Project → Repositories` model working.

## Step 2

Introduce:

```text
Workspace
Team
ProjectArea
Repository
RepositoryMembership
```

with database migrations.

## Step 3

Change vector payloads from a single `project_id` to scoped workspace/team/project-area/repository metadata.

## Step 4

Index a physical repository once and attach project-area memberships.

## Step 5

Populate Neo4j with ownership and project/repository relationships.

## Step 6

Add Tree-sitter extraction for actual source relationships.

## Step 7

Resolve cross-repository APIs/imports/events/contracts.

## Step 8

Add scope-aware MCP tools.

Examples:

```text
search_project_knowledge
search_team_knowledge
trace_cross_repo_dependency
find_repository_consumers
analyze_change_impact
```

These are proposed future MCP APIs.

---

# Can the current CodeDevX code be extended to this model?

**Yes.**

The existing separation between PostgreSQL state, Qdrant retrieval, Neo4j graph storage, knowledge adapters, model providers and MCP makes this extension practical.

However, the hierarchy described here should be implemented as an explicit data-model evolution rather than encoding team/project relationships into repository names or prompts.

The recommended long-term structure is:

```text
Workspace
  ↓
Teams
  ↓
Project Areas
  ↓
Repository Membership
  ↓
Physical Repositories
  ↓
Symbols / APIs / Events / Data
  ↓
Cross-repository Graph
  ↓
Hybrid RAG
  ↓
MCP
  ↓
AI-DLC / Coding Agents / Domain Expert / Support Agent
```
