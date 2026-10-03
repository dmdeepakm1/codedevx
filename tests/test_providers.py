from codedevx.config import settings
from codedevx.embeddings.router import EmbeddingRouter
from codedevx.llm.router import ProviderRouter

def test_provider_aliases(monkeypatch):
    monkeypatch.setattr(settings,"anthropic_api_key","test")
    provider=ProviderRouter().provider("claude")
    assert provider.__class__.__name__=="AnthropicProvider"

def test_embedding_router_rejects_unknown():
    try:
        EmbeddingRouter().provider("unknown")
    except ValueError as exc:
        assert "Embedding provider not configured" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
