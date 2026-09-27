from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6"
    embedding_model: str = "text-embedding-3-small"
    postgres_url: str = "postgresql+psycopg://codedevx:codedevx@localhost:5432/codedevx"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "codedevx_code"
    max_context_chunks: int = 12

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CODEDEVX_", extra="ignore")

    def model_post_init(self, __context):
        import os
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

settings = Settings()
