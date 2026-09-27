# Local Setup — V1, V2 and V3

Follow this guide sequentially: verify V1 first, then V2, then V3.

## Common prerequisites

Required:
- Git
- Python 3.11+
- Podman Desktop or Podman CLI
- OpenAI API key for the current embedding implementation

Optional:
- Ollama for local generation
- Neo4j graph retrieval in V2/V3

Check:
```bash
git --version
python3.11 --version
podman --version
podman compose version
```

Clone and install:
```bash
git clone https://github.com/dmdeepakm1/codedevx.git
cd codedevx
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
cp .env.example .env
```

Add your API key to `.env` and never commit it:
```bash
OPENAI_API_KEY=<your-key>
```

Start infrastructure:
```bash
podman compose up -d
podman ps
pytest
```

## V1 — multi-repository code RAG

Set in `.env`:
```bash
CODEDEVX_VERSION=1
CODEDEVX_GRAPH_ENABLED=false
```

Verify:
```bash
codedevx version
```

Register a project and local Git repositories:
```bash
codedevx project-add sample-platform
codedevx repo-add sample-platform web-app /absolute/path/to/web-app frontend
codedevx repo-add sample-platform product-api /absolute/path/to/product-api backend
codedevx repo-add sample-platform shared-sdk /absolute/path/to/shared-sdk shared
```

Index:
```bash
codedevx index sample-platform
```

Ask:
```bash
codedevx ask sample-platform "Explain the main modules and where API calls are implemented"
```

Smoke test:
1. Ask about a known class/file.
2. Change and commit one source file locally.
3. Run the index command again.
4. Verify only changed files/chunks are processed.

## V2 — knowledge, hybrid RAG, Ollama and MCP

Set:
```bash
CODEDEVX_VERSION=2
```

Optional graph lookup:
```bash
CODEDEVX_GRAPH_ENABLED=true
```

### Add knowledge

Current document ingestion supports Markdown.

Example:
```text
knowledge/
├── architecture.md
├── api-design.md
├── adr-001.md
└── operations-runbook.md
```

Index:
```bash
codedevx knowledge-add sample-platform /absolute/path/to/knowledge
```

Ask:
```bash
codedevx ask sample-platform "Explain the architecture and show the code that implements it"
```

### Optional Ollama

Install Ollama separately using its supported installer, start it and install a coding model. Check:
```bash
ollama --version
ollama list
```

Set the exact installed model:
```bash
CODEDEVX_OLLAMA_URL=http://localhost:11434
CODEDEVX_OLLAMA_MODEL=<installed-model-name>
```

Test:
```bash
codedevx ask sample-platform "Explain this project's architecture" --provider ollama
```

Current limitation: Ollama can be used for generation, but the current vector-store implementation still uses OpenAI embeddings.

### Neo4j

Local browser:
```text
http://localhost:7474
```

Graph lookup exists, but complete AST/call/dependency population is not implemented yet. Enabling graph retrieval does not create missing source relationships.

### MCP

Start:
```bash
codedevx-mcp
```

Current MCP tools:
```text
search_engineering_knowledge
get_aidlc_context
```

## V3 — agent-development profile

Set:
```bash
CODEDEVX_VERSION=3
```

V3 reuses V2 retrieval and currently provides guarded workspace primitives:
- workspace-contained reads/writes;
- allow-listed development commands;
- command timeout;
- bounded stdout/stderr.

The complete autonomous flow below is not implemented yet:
```text
plan → edit → build → test → diagnose → repair → approval → PR
```

Use V3 as the foundation for that coding agent.

## Stop services

```bash
podman compose down
```

To intentionally delete local volumes:
```bash
podman compose down -v
```

## Troubleshooting

Services:
```bash
podman ps
podman compose logs
```

CLI:
```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

Ollama:
```bash
ollama list
```

Sparse graph results are expected until AST/Tree-sitter relationship extraction is implemented.

There is currently no direct Jira/Confluence connector in CodeDevX. For the local POC, use Markdown exports. External Atlassian/Rovo MCP integration is part of the target architecture.
