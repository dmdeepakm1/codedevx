# Integrated Architecture: CodeDevX + AI-DLC + External MCP Knowledge

## Architectural decision

CodeDevX does **not** implement a second lifecycle engine.

Responsibilities are separated:

| Component | Owns |
|---|---|
| AI-DLC workflow | specification-driven stages, clarification questions, user answers, approvals/gates, lifecycle state, generated artifacts |
| CodeDevX | engineering evidence, code intelligence, relationships, provenance, impact context, hybrid retrieval |
| External Atlassian/Rovo MCP | permission-aware Jira/Confluence access where approved/configured |
| LLM/coding harness | reasoning/generation/tool use subject to workflow gates |

```text
User
 │
 ▼
AI-DLC / Spec-driven workflow
 │
 ├── asks clarification questions
 ├── records user decisions
 ├── creates/updates specification
 └── enforces approval gates
 │
 ▼
CodeDevX MCP
 │
 ├── search_engineering_knowledge
 └── get_aidlc_context
 │
 ├──────── Code analysis
 │
 ├──────── Qdrant
 │
 ├──────── Neo4j
 │
 └──────── external knowledge adapters/MCP
               │
               └── Jira / Confluence / other approved sources
```

## Evidence before relationships

Every durable relationship should carry provenance. A relationship should not become "fact" merely because a model inferred it.

Examples:

```text
web-component --CALLS_API--> product-api
evidence:
  source = code_analysis
  revision = git SHA

service --DOCUMENTED_BY--> architecture-page
evidence:
  source = mcp/documentation
  source_id = external document ID
  revision = document version

implementation --RELATED_TO_WORK_ITEM--> requirement
evidence:
  source = work_item
  source_id = work-item ID
```

Model-derived relationships should use `MODEL_INFERENCE`, a confidence value, and normally `requires_confirmation=true`.

## Relationship sources

| Relationship | Preferred evidence |
|---|---|
| CONTAINS | repository/code analysis |
| IMPORTS | AST/code analysis |
| CALLS | AST/CPG/code analysis |
| IMPLEMENTS | AST/code analysis |
| EXTENDS | AST/code analysis |
| DEPENDS_ON | code/build/config; documentation as supporting evidence |
| EXPOSES_API | code/OpenAPI |
| CALLS_API | code/OpenAPI |
| READS_FROM | code/config/schema |
| WRITES_TO | code/config/schema |
| PUBLISHES_EVENT | code/config/contracts |
| CONSUMES_EVENT | code/config/contracts |
| TESTED_BY | test/code analysis |
| DOCUMENTED_BY | documentation/MCP |
| RELATED_TO_WORK_ITEM | work-item/MCP |
| IMPLEMENTS_REQUIREMENT | work item + code/PR evidence |
| OWNED_BY | authoritative ownership metadata |
| USED_BY | dependency/membership evidence |
| BLOCKED_BY | work-item system |
| AFFECTS | derived impact analysis; preserve supporting evidence |

## External MCP boundary

Do not bake a vendor-specific Rovo client into the core graph or retrieval model.

Use an adapter boundary:

```text
External MCP source
      │
      ▼
Normalized evidence
      │
      ├── source type
      ├── immutable/source ID
      ├── URI
      ├── revision/version
      ├── timestamps
      ├── project/workspace scope
      └── permission/security metadata
      │
      ▼
CodeDevX ingestion / graph
```

This lets the same architecture accept another approved Jira/Confluence connector later without rewriting the graph.

## Human gates

CodeDevX retrieval is non-authoritative with respect to workflow approval.

```text
AI-DLC stage
   │
   ▼
Need more information?
   │
 ┌─┴───────────────┐
 │ yes             │ no
 ▼                 ▼
Ask user        Retrieve evidence
 │                 │
 ▼                 ▼
Record answer   Generate candidate artifact
       \          /
        ▼        ▼
        User approval gate
               │
       ┌───────┴───────┐
       │ approve       │ revise
       ▼               ▼
   next stage      questions/rework
```

A model or CodeDevX tool must not silently approve an AI-DLC gate.

## Spec-driven integration

Treat the approved specification as an input to retrieval rather than storing lifecycle control inside CodeDevX.

Example:

```text
Approved requirement/spec
       │
       ▼
get_aidlc_context(
  project_id,
  stage="design",
  requirement=<approved spec>
)
       │
       ▼
CodeDevX evidence
       │
       ▼
AI-DLC generates candidate HLD
       │
       ▼
User approval
```

The same pattern applies to design, implementation planning, testing and review.

## Current code

Implemented in CodeDevX:

- `Relationship`, `RelationType`, `Evidence` and `EvidenceSource`
- provenance requirement for typed relationships
- verified-vs-inferred distinction
- `AIDLCContextService`
- MCP `get_aidlc_context`
- existing MCP `search_engineering_knowledge`

Not implemented by this change:

- a direct Rovo/Atlassian MCP client;
- AI-DLC workflow/gate execution;
- Jira/Confluence synchronization;
- Tree-sitter/Joern extraction;
- persistence of the new typed `Relationship` objects into Neo4j;
- permission-aware external document caching.

Those require dedicated follow-on implementations and environment-specific authentication.

## Next implementation priorities

1. Persist typed relationships and evidence in Neo4j.
2. Add workspace/team/project-area scope to storage and retrieval.
3. Add a generic external-MCP evidence adapter.
4. Add permission/security metadata and retrieval filtering.
5. Add Tree-sitter source extraction.
6. Reconcile code-derived and documentation-derived relationships without overwriting provenance.
7. Add retrieval evaluation/golden tests.
8. Plug CodeDevX MCP into the selected AI-DLC harness and validate clarification/approval behavior end-to-end.
