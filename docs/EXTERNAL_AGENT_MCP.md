# External AI agents and CodeDevX

CodeDevX uses MCP as the interoperability boundary for external coding agents.

## Key rule

Claude Code, Kiro, Copilot, or another MCP-capable IDE agent owns its own model authentication. Do not put that client's model credential into CodeDevX merely to use CodeDevX tools.

The external client starts or connects to:

```bash
codedevx-mcp
```

CodeDevX exposes:

- `search_engineering_knowledge`
- `get_aidlc_context`

The client can use those tools while keeping its own model/runtime independent.

## Direct inference vs external MCP client

| Mode | CodeDevX credential |
|---|---|
| Claude/Kiro/Copilot uses CodeDevX over MCP | no client model key in CodeDevX |
| `codedevx ask ... --provider openai` | `OPENAI_API_KEY` |
| `codedevx ask ... --provider anthropic` | `ANTHROPIC_API_KEY` |
| `codedevx ask ... --provider ollama` | local Ollama |
| indexing with OpenAI embeddings | `OPENAI_API_KEY` |
| indexing with Ollama embeddings | local Ollama |

## Local setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
codedevx doctor
codedevx-mcp
```

For a no-cloud-key local retrieval POC:

```bash
CODEDEVX_EMBEDDING_PROVIDER=ollama
CODEDEVX_OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

Pull that model in Ollama before indexing.

## MCP client configuration

Exact configuration format differs by Claude Code, Kiro, Copilot and IDE version. Configure the client to launch the `codedevx-mcp` executable from the CodeDevX virtual environment. Keep client-specific files outside CodeDevX core unless they are safe example templates.

## Security

Never commit real API keys, Jira/Confluence tokens, GitHub tokens, customer data exports, or a populated `.env`.
