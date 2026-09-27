# CodeDevX

Extensible multi-project, multi-repository engineering intelligence and coding-agent starter.

## Goals
- Multiple projects, each containing multiple Git repositories
- Incremental indexing by Git SHA / changed files
- Cheap deterministic code indexing before LLM usage
- Vector search with Qdrant
- Provider-neutral LLM layer: OpenAI now, Claude/Ollama/llama.cpp later
- Frontend + backend repositories in the same project
- Persistent project/repository/index state in PostgreSQL

## Quick start

1. Copy `.env.example` to `.env`
2. Set `OPENAI_API_KEY`
3. Start infrastructure with `podman compose up -d`
4. Create a Python virtual environment and run `pip install -e .`
5. Register a project and its repositories with the `codedevx` CLI
6. Run `codedevx index <project>`
7. Ask questions with `codedevx ask <project> "<question>"`

Indexing avoids chat-model calls. Only changed chunks are embedded, and reasoning is invoked after retrieval narrows context.
