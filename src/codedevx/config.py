from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    version:int=1
    openai_api_key:str=""
    openai_model:str="gpt-5.6"
    anthropic_api_key:str=""
    anthropic_model:str="claude-sonnet-4-5"
    embedding_provider:str="openai"
    embedding_model:str="text-embedding-3-small"
    postgres_url:str="postgresql+psycopg://codedevx:codedevx@localhost:5432/codedevx"
    qdrant_url:str="http://localhost:6333"
    qdrant_collection:str="codedevx_code"
    max_context_chunks:int=24
    max_context_tokens:int=20000
    graph_enabled:bool=False
    strict_integrations:bool=False
    neo4j_uri:str="bolt://localhost:7687"
    neo4j_user:str="neo4j"
    neo4j_password:str="codedevx-local"
    neo4j_database:str="neo4j"
    ollama_url:str="http://localhost:11434"
    ollama_model:str="qwen3-coder"
    ollama_embedding_model:str="nomic-embed-text"
    llm_timeout_seconds:int=180
    model_config=SettingsConfigDict(env_file=".env",env_prefix="CODEDEVX_",extra="ignore")

    def model_post_init(self,__context):
        import os
        if not self.openai_api_key:self.openai_api_key=os.getenv("OPENAI_API_KEY","")
        if not self.anthropic_api_key:self.anthropic_api_key=os.getenv("ANTHROPIC_API_KEY","")

settings=Settings()
