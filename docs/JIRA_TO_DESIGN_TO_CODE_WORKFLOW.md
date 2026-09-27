# Jira → Reverse Engineering → HLD/LLD → Approval → Code

## What this means

The target experience is:

```text
Jira work item
      ↓
AI-DLC / spec-driven workflow
      ↓
clarifying questions
      ↓
user answers
      ↓
approved requirement/spec
      ↓
CodeDevX engineering evidence
      ↓
reverse engineering + impact analysis
      ↓
candidate HLD
      ↓
USER APPROVAL
      ↓
candidate LLD
      ↓
USER APPROVAL
      ↓
implementation plan
      ↓
USER APPROVAL
      ↓
coding agent
      ↓
edit → build → test → bounded repair
      ↓
diff/test evidence
      ↓
user review / PR
```

This complete automated gated lifecycle is **not implemented yet**. AI-DLC should own lifecycle stages, questions and approval gates. CodeDevX should provide grounded engineering evidence.

## What CodeDevX can do today

- index multiple source repositories;
- retrieve project-scoped source-code chunks;
- ingest Markdown architecture/ADR/runbook knowledge;
- combine vector and optional graph evidence;
- expose engineering retrieval through MCP;
- expose AI-DLC context through `get_aidlc_context`;
- use OpenAI or Ollama for generation.

## Reverse engineering

For a requirement, CodeDevX should retrieve:
- relevant repositories;
- architecture documents;
- classes/functions;
- APIs;
- data stores;
- events/contracts;
- shared libraries;
- tests;
- related work items;
- operational documentation.

The goal is an evidence-backed current-state architecture. Complete automatic reconstruction requires the planned AST/Tree-sitter and graph work.

## HLD

A candidate HLD should use:
```text
approved requirement
+ existing architecture evidence
+ impact analysis
+ ADR/design knowledge
+ constraints
```

Typical sections:
1. problem/context;
2. existing architecture;
3. proposed architecture;
4. affected components;
5. APIs/events/data;
6. security;
7. scalability;
8. compatibility;
9. dependencies;
10. risks;
11. alternatives;
12. rollout.

Existing-system claims must come from retrieved evidence.

## LLD

After HLD approval, retrieve deeper source context and generate a candidate LLD covering:
- affected repositories;
- files/modules;
- classes/interfaces;
- methods/functions;
- API contracts;
- DTO/schema changes;
- validation/error handling;
- configuration;
- logging/telemetry;
- unit/integration tests;
- migration/compatibility.

Anything not supported by evidence should be marked for confirmation.

## Implementation plan

After design approval, create a repository-scoped plan, for example:
```text
web-app
- update component
- update API client
- add tests

product-api
- update validation service
- map error response
- add unit/integration tests

shared-sdk
- update shared contract if required
```

The approved plan becomes input to the coding stage.

## Coding target

```text
Approved spec + HLD + LLD + plan
               ↓
          Coding agent
               ↓
              edit
               ↓
          build / test
          ↙         ↘
       pass         fail
        ↓             ↓
    final diff     diagnose
                      ↓
                    repair
                      ↓
                  build/test
```

V3 has guarded workspace primitives, but this complete loop remains future work.

## Jira and Confluence

Preferred target:
```text
Atlassian/Rovo MCP
      ↓
Jira + Confluence
      ↓
normalized evidence with provenance
      ↓
CodeDevX
   ↙       ↘
Qdrant    Neo4j
      ↓
AI-DLC context
```

Do not make vendor-specific Atlassian objects the core domain model. Normalize external content into evidence containing source ID, URI, revision, scope and permission metadata.

## Local POC today

1. Clone the relevant repositories.
2. Register/index them in V1.
3. Export relevant requirements/architecture to Markdown.
4. Add that knowledge in V2.
5. Ask CodeDevX to analyze the requirement against code and documentation.
6. Use `get_aidlc_context` as evidence input to AI-DLC.
7. Review the candidate design manually.
8. Approve HLD/LLD/implementation plan outside CodeDevX.
9. Feed the approved implementation plan to your coding harness.

This preserves human gates while the direct integrations are being built.

## Example prompts

Requirement analysis:
```text
Analyze this requirement against the indexed project.
Identify relevant repositories, existing implementation, constraints,
tests and missing information. Separate evidence from inference.

<requirement>
...
</requirement>
```

Reverse engineering:
```text
Using only retrieved project evidence, describe the current architecture
related to this requirement. Include repository/file references and state
where evidence is insufficient.
```

Candidate HLD:
```text
Using the approved requirement and retrieved current-state evidence,
prepare a candidate HLD. Clearly distinguish current architecture from
proposed changes. Do not invent existing components.
```

Candidate LLD:
```text
Using the approved HLD and retrieved source evidence, prepare a candidate
LLD listing affected repositories, modules/classes, interfaces, API/data
changes and tests. Mark anything requiring user confirmation.
```

Implementation plan:
```text
Using the approved requirement, HLD and LLD, create an implementation
plan grouped by repository. Do not modify code yet.
```

## Responsibility boundary

```text
CodeDevX
- what exists?
- where is it?
- how is it related?
- what may be impacted?
- what evidence supports this?

AI-DLC
- what stage are we in?
- what questions must be answered?
- has the user approved the artifact?
- what specification is authoritative?
- can implementation proceed?
```

## Next implementation priorities

1. Tree-sitter AST extraction.
2. Cross-repository graph population.
3. Typed relationship persistence with provenance.
4. Workspace/team/project-area scoping.
5. External MCP evidence adapter for Jira/Confluence.
6. AI-DLC harness integration.
7. Artifact version/provenance for requirement/HLD/LLD/plan.
8. Human approval state supplied by AI-DLC.
9. V3 coding loop with worktree isolation.
10. Build/test/repair limits and final diff.
