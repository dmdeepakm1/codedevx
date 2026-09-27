# CodeDevX

Model-independent engineering knowledge and coding-agent platform for multiple projects and repositories.

## Runtime profiles

Set `CODEDEVX_VERSION` in `.env`:

- **V1 / 1** — multi-project/multi-repo code indexing, PostgreSQL state, Qdrant code RAG, OpenAI.
- **V2 / 2** — V1 plus document knowledge ingestion, hybrid vector/graph retrieval, Neo4j, Ollama fallback, MCP server.
- **V3 / 3** — V2 plus guarded workspace primitives intended for coding/build/test agents. Agent clients remain adapters; organizational knowledge stays outside the model.

Features are additive, so V3 can consume V1/V2 data.

## Install on macOS

Prerequisites: Python 3.11+, Git, Podman Desktop or Podman CLI. Ollama is optional for local inference.

```bash
git clone https://github.com/dmdeepakm1/codedevx.git
cd codedevx
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
podman compose up -d
```

For local Ollama, install Ollama separately, start it, and pull a coding model that exists in your Ollama registry. Set `CODEDEVX_OLLAMA_MODEL` to that exact model name. CodeDevX deliberately does not auto-download models.

## V1

```bash
# .env: CODEDEVX_VERSION=1
codedevx project-add cx360
codedevx repo-add cx360 frontend /absolute/path/to/frontend frontend
codedevx repo-add cx360 backend /absolute/path/to/backend backend
codedevx index cx360
codedevx ask cx360 "Trace product loading from UI to backend"
```

## V2: knowledge + hybrid RAG

Put Markdown exports/ADRs/runbooks under a local directory:

```bash
# .env: CODEDEVX_VERSION=2
# optional: CODEDEVX_GRAPH_ENABLED=true
codedevx knowledge-add cx360 /absolute/path/to/knowledge
codedevx ask cx360 "Explain the design and show relevant code"
codedevx ask cx360 "Explain the design" --provider ollama
```

Current document adapter is Markdown. Confluence/Jira should be added through authenticated organization-specific adapters or MCP rather than embedding credentials into this repository.

## MCP

Run the CodeDevX MCP server:

```bash
codedevx-mcp
```

It exposes `search_engineering_knowledge(project_id, query, limit)`. MCP-capable coding clients can use this as their knowledge interface. Client-specific Claude/Kiro configuration is intentionally not hard-coded because authentication and supported MCP configuration vary by client/version.

## V3

V3 retains the same knowledge and retrieval layers and adds guarded workspace operations for future coding agents. File access is workspace-contained and executable commands are allow-listed. Keep write/build/test agents in disposable branches/worktrees and CI; do not grant arbitrary shell execution to an LLM.

## Infrastructure

`compose.yaml` runs PostgreSQL, Qdrant and Neo4j with Podman/Docker-compatible images. The bundled credentials are local-development defaults only. Replace passwords, use secret management, TLS, backups and network controls before shared deployment.

## What is deliberately not claimed

This repository is a production-oriented baseline, not a claim that every enterprise integration is production-certified. Confluence/Jira authentication, Claude/Kiro client wiring, SSO, HA, observability, RBAC, backups, CI policies and organization security controls require environment-specific configuration and validation.

## Next adapters

The extension points are intentionally separated:
- LLM: `src/codedevx/llm/`
- Knowledge: `src/codedevx/knowledge/`
- Retrieval: `src/codedevx/retrieval/`
- Graph: `src/codedevx/graph/`
- MCP: `src/codedevx/mcp/`
- Agent tools: `src/codedevx/tools/`

Never commit `.env`, API tokens, Jira/Confluence tokens or model-provider credentials.
